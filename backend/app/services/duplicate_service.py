"""
Duplicate detection: non-LLM fuzzy pre-filter (rapidfuzz, grouped by theme)
shortlists candidate pairs, then duplicate_confirm_prompt confirms which
candidates are true duplicates, then union-find turns confirmed pairs into
N-member groups. No embeddings/vector search anywhere in this path.
"""

import itertools
import uuid
from collections import defaultdict

from rapidfuzz import fuzz
from sqlalchemy.orm import Session

from app.db.models.duplicate import DuplicateGroup, DuplicateGroupMember
from app.db.models.feedback import Feedback
from app.services import ai_service

FUZZY_SHORTLIST_THRESHOLD = 35
THEME_BUCKET_ALL_PAIRS_CAP = 30
CONFIRM_BATCH_SIZE = 15


class _UnionFind:
    def __init__(self, ids: list[uuid.UUID]):
        self.parent = {i: i for i in ids}

    def find(self, x: uuid.UUID) -> uuid.UUID:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: uuid.UUID, b: uuid.UUID) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def _shortlist_candidate_pairs(
    feedback_by_theme: dict[str, list[tuple[uuid.UUID, str]]]
) -> list[tuple[uuid.UUID, uuid.UUID]]:
    """
    Grouping by theme already does the real cost-cutting (full-batch O(n^2) ->
    per-theme O(k^2) with k usually small), so within a normally-sized theme
    bucket we send EVERY pair to the LLM confirmation rather than pre-filtering
    on lexical similarity — true duplicates are frequently worded completely
    differently ("Unable to login" vs "Login failed again"), and a strict
    token-overlap score would silently drop them before the LLM ever sees them,
    which defeats the point of using an LLM for this step. The fuzzy score is
    only applied as a last-resort cost cap for pathologically large theme
    buckets, where the LLM confirmation step is the real safety net for
    precision — recall at this shortlisting stage matters more.
    """
    candidates = []
    for _theme, rows in feedback_by_theme.items():
        if len(rows) <= THEME_BUCKET_ALL_PAIRS_CAP:
            candidates.extend(
                (id_a, id_b) for (id_a, _), (id_b, _) in itertools.combinations(rows, 2)
            )
            continue
        for (id_a, text_a), (id_b, text_b) in itertools.combinations(rows, 2):
            score = fuzz.token_sort_ratio(text_a.lower(), text_b.lower())
            if score >= FUZZY_SHORTLIST_THRESHOLD:
                candidates.append((id_a, id_b))
    return candidates


def run_duplicate_detection(
    db: Session, *, upload_id: uuid.UUID, feedback_rows: list[Feedback], themes_by_feedback_id: dict[uuid.UUID, str]
) -> int:
    """
    feedback_rows: non-duplicate feedback belonging to this upload.
    themes_by_feedback_id: feedback_id -> theme, from the just-computed classifications.
    Returns the number of duplicate groups created.
    """
    feedback_by_theme: dict[str, list[tuple[uuid.UUID, str]]] = defaultdict(list)
    text_by_id: dict[uuid.UUID, str] = {}
    for row in feedback_rows:
        theme = themes_by_feedback_id.get(row.id, "Other")
        text = row.cleaned_text or row.raw_text
        feedback_by_theme[theme].append((row.id, text))
        text_by_id[row.id] = text

    candidate_pairs = _shortlist_candidate_pairs(feedback_by_theme)
    if not candidate_pairs:
        return 0

    confirmed_pairs: list[tuple[uuid.UUID, uuid.UUID]] = []
    for batch_start in range(0, len(candidate_pairs), CONFIRM_BATCH_SIZE):
        batch = candidate_pairs[batch_start : batch_start + CONFIRM_BATCH_SIZE]
        payload = [
            {
                "pair_id": f"{a}|{b}",
                "item_a_id": str(a),
                "item_b_id": str(b),
                "item_a": text_by_id[a],
                "item_b": text_by_id[b],
            }
            for a, b in batch
        ]
        confirmations = ai_service.confirm_duplicates(payload)
        for a, b in batch:
            is_dup, _confidence, _reason = confirmations.get(f"{a}|{b}", (False, 0, ""))
            if is_dup:
                confirmed_pairs.append((a, b))

    if not confirmed_pairs:
        return 0

    all_ids = {i for pair in confirmed_pairs for i in pair}
    uf = _UnionFind(list(all_ids))
    for a, b in confirmed_pairs:
        uf.union(a, b)

    groups: dict[uuid.UUID, list[uuid.UUID]] = defaultdict(list)
    for member_id in all_ids:
        groups[uf.find(member_id)].append(member_id)

    groups_created = 0
    for root, member_ids in groups.items():
        if len(member_ids) < 2:
            continue
        representative_id = min(member_ids, key=lambda i: str(i))
        group = DuplicateGroup(
            upload_id=upload_id,
            representative_feedback_id=representative_id,
            similarity_method="fuzzy_text_llm_confirmed",
        )
        db.add(group)
        db.flush()
        for member_id in member_ids:
            db.add(DuplicateGroupMember(group_id=group.id, feedback_id=member_id))
            if member_id != representative_id:
                db.query(Feedback).filter(Feedback.id == member_id).update(
                    {"is_duplicate_of": representative_id}
                )
        groups_created += 1

    db.commit()
    return groups_created
