import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    pass


class DuplicateGroup(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "duplicate_groups"

    upload_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("uploads.id"), nullable=False, index=True
    )
    representative_feedback_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("feedback.id"), nullable=False
    )
    similarity_method: Mapped[str] = mapped_column(String(30), nullable=False)  # 'fuzzy_text'
    similarity_score: Mapped[float | None] = mapped_column(Numeric(4, 3), nullable=True)

    members: Mapped[list["DuplicateGroupMember"]] = relationship(back_populates="group")


class DuplicateGroupMember(Base):
    __tablename__ = "duplicate_group_members"

    group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("duplicate_groups.id"), primary_key=True
    )
    feedback_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("feedback.id"), primary_key=True
    )

    group: Mapped["DuplicateGroup"] = relationship(back_populates="members")
