import datetime
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.feedback import Feedback
    from app.db.models.user import User


class Upload(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """One analysis session: a single feedback submission, a pasted batch, or a CSV file."""

    __tablename__ = "uploads"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    source_type: Mapped[str] = mapped_column(String(20), nullable=False)  # single | paste | csv
    original_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    # pending | processing | completed | failed | partial
    current_stage: Mapped[str | None] = mapped_column(String(40), nullable=True)

    total_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    processed_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    completed_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user: Mapped["User"] = relationship(back_populates="uploads")
    feedback_items: Mapped[list["Feedback"]] = relationship(back_populates="upload")
