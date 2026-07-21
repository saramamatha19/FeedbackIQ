"""
Pydantic models mirroring every prompt module's JSON schema.

These are the independent, code-level re-validation layer behind OpenAI's
structured-output guarantee — defense in depth against SDK/version drift,
not a duplicate of the same trust boundary. Any prompt module that returns
data failing validation here is treated as a malformed response and goes
through the shared retry/fallback path in retry.py.
"""

from pydantic import BaseModel, Field

from app.prompts._shared.canonical_themes import CANONICAL_THEMES

CATEGORY_VALUES = ["Bug", "Feature Request", "Complaint", "Praise", "Question", "Other"]
SENTIMENT_VALUES = ["Positive", "Negative", "Neutral", "Mixed"]
EMOTION_VALUES = [
    "Frustration",
    "Anger",
    "Confusion",
    "Satisfaction",
    "Delight",
    "Disappointment",
    "Neutral",
]
URGENCY_VALUES = ["Low", "Medium", "High", "Critical"]
SEVERITY_VALUES = ["Minor", "Moderate", "Major", "Blocker"]
BUSINESS_IMPACT_VALUES = ["None", "Low", "Medium", "High"]
INTENT_VALUES = [
    "Report Issue",
    "Request Feature",
    "Express Opinion",
    "Ask Question",
    "Other",
]


class ClassificationResult(BaseModel):
    id: str | None = None  # present in batch mode to match input item back to output
    category: str
    sentiment: str
    emotion: str
    urgency: str
    severity: str
    business_impact: str
    intent: str
    theme: str
    confidence: int = Field(..., ge=0, le=100)
    explanation: str = Field(..., max_length=300)
    suggested_action: str = Field(..., max_length=200)
    needs_human_review: bool

    def validate_enums(self) -> list[str]:
        """Returns a list of field-level violations; empty list means valid."""
        errors = []
        if self.category not in CATEGORY_VALUES:
            errors.append(f"category '{self.category}' not in allowed set")
        if self.sentiment not in SENTIMENT_VALUES:
            errors.append(f"sentiment '{self.sentiment}' not in allowed set")
        if self.emotion not in EMOTION_VALUES:
            errors.append(f"emotion '{self.emotion}' not in allowed set")
        if self.urgency not in URGENCY_VALUES:
            errors.append(f"urgency '{self.urgency}' not in allowed set")
        if self.severity not in SEVERITY_VALUES:
            errors.append(f"severity '{self.severity}' not in allowed set")
        if self.business_impact not in BUSINESS_IMPACT_VALUES:
            errors.append(f"business_impact '{self.business_impact}' not in allowed set")
        if self.intent not in INTENT_VALUES:
            errors.append(f"intent '{self.intent}' not in allowed set")
        if self.theme not in CANONICAL_THEMES:
            errors.append(f"theme '{self.theme}' not in canonical taxonomy")
        return errors


class ClassificationBatchResult(BaseModel):
    results: list[ClassificationResult]


class SplitItem(BaseModel):
    text: str
    detected_separator_style: str


class SplitResult(BaseModel):
    items: list[SplitItem]


class DuplicateConfirmResult(BaseModel):
    pair_id: str
    item_a_id: str
    item_b_id: str
    is_duplicate: bool
    confidence: int = Field(..., ge=0, le=100)
    reasoning: str = Field(..., max_length=200)


class DuplicateConfirmBatchResult(BaseModel):
    results: list[DuplicateConfirmResult]


class KeySignal(BaseModel):
    headline: str = Field(..., max_length=100)
    detail: str = Field(..., max_length=250)
    supporting_theme: str
    severity_hint: str


class KeySignalsResult(BaseModel):
    signals: list[KeySignal] = Field(..., min_length=3, max_length=3)


class NLQueryFilter(BaseModel):
    themes: list[str] = Field(default_factory=list)
    sentiments: list[str] = Field(default_factory=list)
    urgencies: list[str] = Field(default_factory=list)
    date_from: str | None = None
    date_to: str | None = None
    only_duplicates: bool = False
    only_contradictions: bool = False
    only_needs_review: bool = False
    keyword: str | None = None
