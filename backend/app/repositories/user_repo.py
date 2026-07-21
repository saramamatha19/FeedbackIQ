import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.user import User


def get_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email.lower()))


def get_by_id(db: Session, user_id: uuid.UUID) -> User | None:
    return db.get(User, user_id)


def create(db: Session, *, email: str, hashed_password: str, full_name: str | None) -> User:
    user = User(email=email.lower(), hashed_password=hashed_password, full_name=full_name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def list_all(db: Session, *, limit: int = 100, offset: int = 0) -> list[User]:
    return list(
        db.scalars(select(User).order_by(User.created_at.desc()).limit(limit).offset(offset))
    )
