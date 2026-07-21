import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db.models.feedback import Feedback
from app.db.models.prediction import AIPrediction


def create_many(db: Session, *, upload_id: uuid.UUID, user_id: uuid.UUID, texts: list[str]) -> list[Feedback]:
    rows = [
        Feedback(upload_id=upload_id, user_id=user_id, raw_text=text, source_row_number=i)
        for i, text in enumerate(texts)
    ]
    db.add_all(rows)
    db.commit()
    for row in rows:
        db.refresh(row)
    return rows


def get(db: Session, feedback_id: uuid.UUID, user_id: uuid.UUID) -> Feedback | None:
    return db.scalar(
        select(Feedback).where(Feedback.id == feedback_id, Feedback.user_id == user_id)
    )


def list_for_upload(db: Session, upload_id: uuid.UUID) -> list[Feedback]:
    return list(db.scalars(select(Feedback).where(Feedback.upload_id == upload_id)))


def current_prediction_for(db: Session, feedback_id: uuid.UUID) -> AIPrediction | None:
    return db.scalar(
        select(AIPrediction).where(
            AIPrediction.feedback_id == feedback_id, AIPrediction.is_current.is_(True)
        )
    )


def list_with_current_predictions(
    db: Session,
    *,
    user_id: uuid.UUID,
    upload_id: uuid.UUID | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Feedback]:
    stmt = (
        select(Feedback)
        .options(joinedload(Feedback.predictions))
        .where(Feedback.user_id == user_id)
        .order_by(Feedback.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    if upload_id is not None:
        stmt = stmt.where(Feedback.upload_id == upload_id)
    return list(db.scalars(stmt).unique())
