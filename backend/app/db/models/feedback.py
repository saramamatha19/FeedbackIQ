import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.prediction import AIPrediction
    from app.db.models.upload import Upload


class Feedback(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Raw + cleaned feedback text. Immutable once created — never mutated after ingestion."""

    __tablename__ = "feedback"

    upload_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("uploads.id"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )

    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    cleaned_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_row_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    external_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)

    is_duplicate_of: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("feedback.id"), nullable=True
    )

    upload: Mapped["Upload"] = relationship(back_populates="feedback_items")
    predictions: Mapped[list["AIPrediction"]] = relationship(back_populates="feedback")
