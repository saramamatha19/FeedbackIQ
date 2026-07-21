from pydantic import BaseModel, Field

from app.schemas.feedback import FeedbackOut


class NLQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)


class NLQueryResponse(BaseModel):
    filters_applied: dict
    result_count: int
    results: list[FeedbackOut]
