import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

# Import database models
from app.db.models.dashboard import DashboardSnapshot
from app.db.models.upload import Upload
from app.db.models.user import User

# Used while deleting a user (to delete their uploads too)
from app.repositories import upload_repo


# Find a user by email
def get_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email.lower()))


# Create a new user in the database
def create(
    db: Session,
    *,
    email: str,
    hashed_password: str,
    full_name: str | None,
    is_approved: bool = False,
) -> User:

    # Create User object
    user = User(
        email=email.lower(),
        hashed_password=hashed_password,
        full_name=full_name,
        is_approved=is_approved,
    )

    # Save to database
    db.add(user)
    db.commit()

    # Reload user (gets generated fields like id)
    db.refresh(user)

    return user


# Return all users (supports pagination)
def list_all(db: Session, *, limit: int = 100, offset: int = 0) -> list[User]:
    return list(
        db.scalars(
            select(User)
            .order_by(User.created_at.desc())  # newest first
            .limit(limit)                      # maximum rows
            .offset(offset)                    # skip rows
        )
    )


# Find user by UUID
def get(db: Session, user_id: uuid.UUID) -> User | None:
    return db.get(User, user_id)


# Approve a user account
def approve(db: Session, user: User) -> User:
    user.is_approved = True
    db.commit()
    db.refresh(user)
    return user


# Reject (disable) a user account
def reject(db: Session, user: User) -> User:
    user.is_approved = False
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user


# Delete user and all related data
def delete(db: Session, user_id: uuid.UUID) -> None:

    # Find all uploads of this user
    upload_ids = list(
        db.scalars(
            select(Upload.id).where(Upload.user_id == user_id)
        )
    )

    # Delete each upload
    for upload_id in upload_ids:
        upload_repo.delete(db, upload_id)

    # Delete dashboard snapshots
    db.query(DashboardSnapshot).filter(
        DashboardSnapshot.user_id == user_id
    ).delete(synchronize_session=False)

    # Delete the user
    db.query(User).filter(
        User.id == user_id
    ).delete(synchronize_session=False)

    db.commit()