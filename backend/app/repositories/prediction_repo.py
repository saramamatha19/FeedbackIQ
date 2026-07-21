import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.prediction import AIPrediction
from app.prompts._shared.schemas import ClassificationResult


def save_prediction(
    db: Session,
    *,
    feedback_id: uuid.UUID,
    result: ClassificationResult,
    processing_time_ms: int,
    prompt_version: str,
    model_name: str,
    raw_llm_response: str | None = None,
) -> AIPrediction:
    """Inserts a new current prediction, flipping any previous current row to False first —
    this is what makes re-run analysis produce an auditable version history instead of an
    overwrite."""
    db.query(AIPrediction).filter(
        AIPrediction.feedback_id == feedback_id, AIPrediction.is_current.is_(True)
    ).update({"is_current": False})

    prediction = AIPrediction(
        feedback_id=feedback_id,
        category=result.category,
        sentiment=result.sentiment,
        emotion=result.emotion,
        theme=result.theme,
        urgency=result.urgency,
        severity=result.severity,
        business_impact=result.business_impact,
        customer_intent=result.intent,
        confidence_score=result.confidence,
        ai_explanation=result.explanation,
        suggested_action=result.suggested_action,
        needs_human_review=result.needs_human_review,
        processing_time_ms=processing_time_ms,
        prompt_version=prompt_version,
        model_name=model_name,
        raw_llm_response={"raw": raw_llm_response} if raw_llm_response else None,
        is_current=True,
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return prediction


def history_for_feedback(db: Session, feedback_id: uuid.UUID) -> list[AIPrediction]:
    return list(
        db.scalars(
            select(AIPrediction)
            .where(AIPrediction.feedback_id == feedback_id)
            .order_by(AIPrediction.created_at.desc())
        )
    )
