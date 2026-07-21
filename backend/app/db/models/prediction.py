import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.feedback import Feedback


class AIPrediction(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Versioned AI prediction — 1:N from feedback, never overwritten in place.

    Re-running AI analysis inserts a new row and flips the previous current
    row's is_current to False in the same transaction, so prompt-version
    history and drift are always auditable. Exactly one row per feedback_id
    may have is_current=True — enforced by the partial unique index below.
    """

    __tablename__ = "ai_predictions"
    __table_args__ = (
        Index(
            "ux_ai_predictions_current_per_feedback",
            "feedback_id",
            unique=True,
            postgresql_where="is_current = true",
        ),
    )

    feedback_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("feedback.id"), nullable=False, index=True
    )

    category: Mapped[str] = mapped_column(String(30), nullable=False)
    sentiment: Mapped[str] = mapped_column(String(20), nullable=False)
    emotion: Mapped[str] = mapped_column(String(30), nullable=False)
    theme: Mapped[str] = mapped_column(String(50), nullable=False)
    urgency: Mapped[str] = mapped_column(String(20), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    business_impact: Mapped[str] = mapped_column(String(20), nullable=False)
    customer_intent: Mapped[str] = mapped_column(String(40), nullable=False)

    confidence_score: Mapped[int] = mapped_column(Integer, nullable=False)  # 0-100
    ai_explanation: Mapped[str] = mapped_column(Text, nullable=False)
    suggested_action: Mapped[str] = mapped_column(Text, nullable=False)
    needs_human_review: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    processing_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    prompt_version: Mapped[str] = mapped_column(String(30), nullable=False)
    model_name: Mapped[str] = mapped_column(String(50), nullable=False)
    raw_llm_response: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    feedback: Mapped["Feedback"] = relationship(back_populates="predictions")
