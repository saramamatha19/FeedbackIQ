import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.dashboard import DashboardSnapshot
from app.db.models.upload import Upload
from app.db.models.user import User
from app.repositories import upload_repo


def get_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email.lower()))


def create(
    db: Session, *, email: str, hashed_password: str, full_name: str | None, is_approved: bool = False
) -> User:
    user = User(
        email=email.lower(), hashed_password=hashed_password, full_name=full_name, is_approved=is_approved
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def list_all(db: Session, *, limit: int = 100, offset: int = 0) -> list[User]:
    return list(
        db.scalars(select(User).order_by(User.created_at.desc()).limit(limit).offset(offset))
    )


def get(db: Session, user_id: uuid.UUID) -> User | None:
    return db.get(User, user_id)


def approve(db: Session, user: User) -> User:
    user.is_approved = True
    db.commit()
    db.refresh(user)
    return user


def reject(db: Session, user: User) -> User:
    user.is_approved = False
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user


def delete(db: Session, user_id: uuid.UUID) -> None:
    """Deletes a user and everything they own — their uploads (which cascades to
    feedback/predictions/duplicate groups/contradictions/status history via
    upload_repo.delete), their dashboard snapshots, and the user row itself.
    Can be called on an approved/active user, not just a pending one."""
    upload_ids = list(db.scalars(select(Upload.id).where(Upload.user_id == user_id)))
    for upload_id in upload_ids:
        upload_repo.delete(db, upload_id)

    db.query(DashboardSnapshot).filter(DashboardSnapshot.user_id == user_id).delete(synchronize_session=False)
    db.query(User).filter(User.id == user_id).delete(synchronize_session=False)
    db.commit()
