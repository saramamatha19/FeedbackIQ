import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ProcessingStatusHistory(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Append-only audit trail of pipeline stage transitions for one upload."""

    __tablename__ = "processing_status_history"

    upload_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("uploads.id"), nullable=False, index=True
    )
    stage: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # started | completed | failed
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
