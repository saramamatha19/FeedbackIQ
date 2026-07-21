"""
Contradiction detection — v1 heuristic baseline (zero LLM cost), per the
project's MVP scope decision: same theme + opposing (Positive vs Negative)
sentiment within an upload is flagged as a contradiction candidate. The
LLM-confirmation layer described in the design doc (distinguishing a genuine
opinion clash from two unrelated opinions that merely share a theme) is an
explicit stretch goal, added only if time remains — this heuristic alone is
good enough to surface the "opposing opinions" signal the dashboard needs.
"""

import itertools
import uuid
from collections import defaultdict

from sqlalchemy.orm import Session

from app.db.models.contradiction import ContradictionPair
from app.db.models.feedback import Feedback


def run_contradiction_detection(
    db: Session,
    *,
    upload_id: uuid.UUID,
    feedback_rows: list[Feedback],
    themes_by_feedback_id: dict[uuid.UUID, str],
    sentiments_by_feedback_id: dict[uuid.UUID, str],
) -> int:
    by_theme: dict[str, list[uuid.UUID]] = defaultdict(list)
    for row in feedback_rows:
        theme = themes_by_feedback_id.get(row.id)
        if theme and theme != "Other":
            by_theme[theme].append(row.id)

    created = 0
    for theme, ids in by_theme.items():
        positives = [i for i in ids if sentiments_by_feedback_id.get(i) == "Positive"]
        negatives = [i for i in ids if sentiments_by_feedback_id.get(i) == "Negative"]
        for pos_id, neg_id in itertools.product(positives, negatives):
            db.add(
                ContradictionPair(
                    upload_id=upload_id,
                    feedback_id_a=pos_id,
                    feedback_id_b=neg_id,
                    contradiction_type="Opinion Clash",
                    explanation=(
                        f"Both items are about '{theme}' but express opposite sentiment "
                        "(one positive, one negative) — flagged as a heuristic contradiction "
                        "candidate for review."
                    ),
                    confidence_score=0.5,
                )
            )
            created += 1
    db.commit()
    return created
