import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.models.user import User
from app.db.session import get_db
from app.services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("")
def get_dashboard(
    upload_id: uuid.UUID | None = None,
    refresh: bool = False,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not refresh:
        existing = dashboard_service.get_latest_snapshot(db, user_id=user.id, upload_id=upload_id)
        if existing is not None:
            return {"upload_id": upload_id, "generated_at": existing.created_at, "data": existing.snapshot_data}

    snapshot = dashboard_service.refresh_snapshot(db, user_id=user.id, upload_id=upload_id)
    return {"upload_id": upload_id, "generated_at": snapshot.created_at, "data": snapshot.snapshot_data}
