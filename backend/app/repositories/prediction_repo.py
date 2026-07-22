import uuid

from sqlalchemy.orm import Session

from app.db.models.prediction import AIPrediction
from app.prompts._shared.schemas import ClassificationResult


def _deactivate_current(db: Session, feedback_id: uuid.UUID) -> None:
    db.query(AIPrediction).filter(
        AIPrediction.feedback_id == feedback_id, AIPrediction.is_current.is_(True)
    ).update({"is_current": False})


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
    _deactivate_current(db, feedback_id)

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


def copy_prediction(db: Session, *, source: AIPrediction, feedback_id: uuid.UUID) -> AIPrediction:
    """Gives an exact-duplicate feedback row its own current prediction by copying an
    already-computed one, instead of re-calling the LLM for text we've already classified.
    Same current-flip semantics as save_prediction, so versioning/history stay consistent
    if this feedback_id is ever independently re-run later."""
    _deactivate_current(db, feedback_id)

    prediction = AIPrediction(
        feedback_id=feedback_id,
        category=source.category,
        sentiment=source.sentiment,
        emotion=source.emotion,
        theme=source.theme,
        urgency=source.urgency,
        severity=source.severity,
        business_impact=source.business_impact,
        customer_intent=source.customer_intent,
        confidence_score=source.confidence_score,
        ai_explanation=source.ai_explanation,
        suggested_action=source.suggested_action,
        needs_human_review=source.needs_human_review,
        processing_time_ms=0,
        prompt_version=source.prompt_version,
        model_name=source.model_name,
        raw_llm_response={"copied_from_feedback_id": str(source.feedback_id)},
        is_current=True,
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return prediction
