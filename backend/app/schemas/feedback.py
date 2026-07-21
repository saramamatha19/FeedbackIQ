import datetime
import uuid

from pydantic import BaseModel, Field


class SingleFeedbackRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)


class PredictionOut(BaseModel):
    id: uuid.UUID
    category: str
    sentiment: str
    emotion: str
    theme: str
    urgency: str
    severity: str
    business_impact: str
    customer_intent: str
    confidence_score: int
    ai_explanation: str
    suggested_action: str
    needs_human_review: bool
    processing_time_ms: int | None
    prompt_version: str
    model_name: str
    created_at: datetime.datetime

    model_config = {"from_attributes": True, "protected_namespaces": ()}


class FeedbackOut(BaseModel):
    id: uuid.UUID
    upload_id: uuid.UUID
    raw_text: str
    created_at: datetime.datetime
    prediction: PredictionOut | None = None
    source_label: str = ""

    model_config = {"from_attributes": True}


class SingleFeedbackResponse(BaseModel):
    feedback: FeedbackOut
    prediction: PredictionOut
