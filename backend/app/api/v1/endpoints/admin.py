import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import require_admin
from app.db.models.feedback import Feedback
from app.db.models.prediction import AIPrediction
from app.db.models.upload import Upload
from app.db.models.user import User
from app.db.session import get_db
from app.repositories import feedback_repo, upload_repo, user_repo
from app.schemas.auth import UserOut
from app.schemas.feedback import FeedbackOut, PredictionOut
from app.schemas.upload import UploadOut
from app.services import dashboard_service

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[UserOut])
def list_users(
    limit: int = 100, offset: int = 0, db: Session = Depends(get_db), _admin: User = Depends(require_admin)
):
    return user_repo.list_all(db, limit=limit, offset=offset)


@router.get("/usage")
def usage_stats(db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    total_users = db.scalar(select(func.count(User.id)))
    total_uploads = db.scalar(select(func.count(Upload.id)))
    total_feedback = db.scalar(select(func.count(Feedback.id)))
    avg_confidence = db.scalar(
        select(func.avg(AIPrediction.confidence_score)).where(AIPrediction.is_current.is_(True))
    )
    avg_processing_ms = db.scalar(
        select(func.avg(AIPrediction.processing_time_ms)).where(AIPrediction.is_current.is_(True))
    )
    needs_review_count = db.scalar(
        select(func.count(AIPrediction.id)).where(
            AIPrediction.is_current.is_(True), AIPrediction.needs_human_review.is_(True)
        )
    )
    return {
        "total_users": total_users or 0,
        "total_uploads": total_uploads or 0,
        "total_feedback": total_feedback or 0,
        "avg_confidence": round(float(avg_confidence), 1) if avg_confidence is not None else None,
        "avg_processing_time_ms": round(float(avg_processing_ms), 1) if avg_processing_ms is not None else None,
        "needs_review_count": needs_review_count or 0,
    }


@router.get("/dashboard")
def admin_dashboard(db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    return {"data": dashboard_service.build_admin_snapshot(db)}


@router.get("/uploads", response_model=list[UploadOut])
def list_all_uploads(
    limit: int = 100, offset: int = 0, db: Session = Depends(get_db), _admin: User = Depends(require_admin)
):
    return list(
        db.scalars(select(Upload).order_by(Upload.created_at.desc()).limit(limit).offset(offset))
    )


@router.get("/users/{user_id}/uploads", response_model=list[UploadOut])
def list_user_uploads(
    user_id: uuid.UUID,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    return list(
        db.scalars(
            select(Upload)
            .where(Upload.user_id == user_id)
            .order_by(Upload.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
    )


@router.get("/users/{user_id}/feedback", response_model=list[FeedbackOut])
def list_user_feedback(
    user_id: uuid.UUID,
    upload_id: uuid.UUID | None = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    rows = feedback_repo.list_with_current_predictions(
        db, user_id=user_id, upload_id=upload_id, limit=limit, offset=offset
    )
    labels = upload_repo.source_label_map(db, user_id)
    out = []
    for row in rows:
        current = next((p for p in row.predictions if p.is_current), None)
        item = FeedbackOut.model_validate(row)
        item.prediction = PredictionOut.model_validate(current) if current else None
        item.source_label = labels.get(row.upload_id, "")
        out.append(item)
    return out


@router.get("/feedback/{feedback_id}", response_model=FeedbackOut)
def get_any_feedback(feedback_id: uuid.UUID, db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    row = db.get(Feedback, feedback_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")
    current = feedback_repo.current_prediction_for(db, feedback_id)
    item = FeedbackOut.model_validate(row)
    item.prediction = PredictionOut.model_validate(current) if current else None
    return item
