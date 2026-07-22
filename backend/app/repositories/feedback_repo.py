import uuid

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from app.db.models.contradiction import ContradictionPair
from app.db.models.duplicate import DuplicateGroup, DuplicateGroupMember
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


def delete(db: Session, feedback_id: uuid.UUID) -> None:
    """Deletes one feedback row and everything that references it (predictions,
    contradiction pairs, duplicate-group membership) so no FK is left dangling."""
    db.query(AIPrediction).filter(AIPrediction.feedback_id == feedback_id).delete(synchronize_session=False)
    db.query(ContradictionPair).filter(
        or_(ContradictionPair.feedback_id_a == feedback_id, ContradictionPair.feedback_id_b == feedback_id)
    ).delete(synchronize_session=False)
    db.query(Feedback).filter(Feedback.is_duplicate_of == feedback_id).update(
        {"is_duplicate_of": None}, synchronize_session=False
    )

    affected_group_ids = list(
        db.scalars(select(DuplicateGroupMember.group_id).where(DuplicateGroupMember.feedback_id == feedback_id))
    )
    db.query(DuplicateGroupMember).filter(DuplicateGroupMember.feedback_id == feedback_id).delete(
        synchronize_session=False
    )
    for group_id in affected_group_ids:
        remaining_member_ids = list(
            db.scalars(select(DuplicateGroupMember.feedback_id).where(DuplicateGroupMember.group_id == group_id))
        )
        if len(remaining_member_ids) < 2:
            # Bulk delete, not db.delete(group) — an ORM-tracked delete only flushes at
            # commit, which would run after the raw Feedback delete below and violate
            # the representative_feedback_id FK. Bulk statements execute immediately.
            db.query(DuplicateGroupMember).filter(DuplicateGroupMember.group_id == group_id).delete(
                synchronize_session=False
            )
            db.query(DuplicateGroup).filter(DuplicateGroup.id == group_id).delete(synchronize_session=False)
        else:
            db.query(DuplicateGroup).filter(
                DuplicateGroup.id == group_id, DuplicateGroup.representative_feedback_id == feedback_id
            ).update({"representative_feedback_id": remaining_member_ids[0]}, synchronize_session=False)

    db.query(Feedback).filter(Feedback.id == feedback_id).delete(synchronize_session=False)
    db.commit()
