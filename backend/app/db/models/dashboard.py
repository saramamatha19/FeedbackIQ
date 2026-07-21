import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class DashboardSnapshot(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Precomputed aggregate cache — regenerated at end of pipeline so dashboard reads are cheap."""

    __tablename__ = "dashboard_snapshots"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    upload_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("uploads.id"), nullable=True
    )  # null = all-time snapshot for the user
    snapshot_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
