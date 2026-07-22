import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.db.models.user import User
from app.repositories import user_repo


def register_user(db: Session, *, email: str, password: str, full_name: str | None) -> User:
    if user_repo.get_by_email(db, email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists"
        )
    return user_repo.create(
        db, email=email, hashed_password=hash_password(password), full_name=full_name, is_approved=False
    )


def authenticate_user(db: Session, *, email: str, password: str) -> User:
    user = user_repo.get_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password"
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")
    if user.role != "admin" and not user.is_approved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Your account is pending admin approval."
        )
    user.last_login_at = datetime.datetime.now(datetime.timezone.utc)
    db.commit()
    return user


def issue_token_for(user: User) -> str:
    return create_access_token(user.id)
