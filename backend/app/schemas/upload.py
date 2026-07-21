import datetime
import uuid

from pydantic import BaseModel, Field


class PasteFeedbackRequest(BaseModel):
    raw_text: str = Field(..., min_length=1, max_length=50_000)


class UploadStatusOut(BaseModel):
    id: uuid.UUID
    status: str
    current_stage: str | None
    total_rows: int
    processed_rows: int
    failed_rows: int
    error_message: str | None

    model_config = {"from_attributes": True}


class UploadOut(BaseModel):
    id: uuid.UUID
    source_type: str
    original_filename: str | None
    display_name: str | None
    status: str
    current_stage: str | None
    total_rows: int
    processed_rows: int
    failed_rows: int
    created_at: datetime.datetime
    completed_at: datetime.datetime | None

    model_config = {"from_attributes": True}
