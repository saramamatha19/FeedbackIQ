"""
Translates an NLQueryFilter (produced by ai_service.translate_nl_query) into
a parameterized SQLAlchemy query. This module is the actual safety boundary
for natural-language search — not the prompt. Every field/operator used here
is an explicit, hand-written SQLAlchemy expression; nothing from the LLM's
output is ever interpolated into a query string. user_id scoping is applied
here in code, unconditionally, so the LLM's output can never leak another
tenant's data even if it somehow ignored every instruction in the prompt.
"""

import datetime
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.contradiction import ContradictionPair
from app.db.models.feedback import Feedback
from app.db.models.prediction import AIPrediction
from app.prompts._shared.schemas import NLQueryFilter

HARD_RESULT_LIMIT = 500
MAX_KEYWORD_LENGTH = 200


def _safe_date(value: str | None) -> datetime.date | None:
    if not value:
        return None
    try:
        return datetime.date.fromisoformat(value)
    except ValueError:
        return None


def run_nl_query(db: Session, *, user_id: uuid.UUID, nl_filter: NLQueryFilter, limit: int = 100):
    stmt = (
        select(Feedback, AIPrediction)
        .join(AIPrediction, AIPrediction.feedback_id == Feedback.id)
        .where(Feedback.user_id == user_id)  # server-enforced, never LLM-controlled
        .where(AIPrediction.is_current.is_(True))
    )

    if nl_filter.themes:
        stmt = stmt.where(AIPrediction.theme.in_(nl_filter.themes))
    if nl_filter.sentiments:
        stmt = stmt.where(AIPrediction.sentiment.in_(nl_filter.sentiments))
    if nl_filter.urgencies:
        stmt = stmt.where(AIPrediction.urgency.in_(nl_filter.urgencies))

    date_from = _safe_date(nl_filter.date_from)
    if date_from:
        stmt = stmt.where(Feedback.created_at >= date_from)
    date_to = _safe_date(nl_filter.date_to)
    if date_to:
        stmt = stmt.where(Feedback.created_at <= date_to + datetime.timedelta(days=1))

    if nl_filter.only_needs_review:
        stmt = stmt.where(AIPrediction.needs_human_review.is_(True))

    if nl_filter.only_duplicates:
        stmt = stmt.where(Feedback.is_duplicate_of.isnot(None))

    if nl_filter.only_contradictions:
        contradiction_feedback_ids = select(ContradictionPair.feedback_id_a).union(
            select(ContradictionPair.feedback_id_b)
        )
        stmt = stmt.where(Feedback.id.in_(contradiction_feedback_ids))

    if nl_filter.keyword:
        keyword = nl_filter.keyword.strip()[:MAX_KEYWORD_LENGTH].replace("%", "").replace("_", "")
        if keyword:
            stmt = stmt.where(Feedback.cleaned_text.ilike(f"%{keyword}%"))

    safe_limit = min(max(limit, 1), HARD_RESULT_LIMIT)
    stmt = stmt.order_by(Feedback.created_at.desc()).limit(safe_limit)

    return db.execute(stmt).all()
