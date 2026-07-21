"""
summary_prompt.py

Purpose
-------
Produces "This Week's Key Signals" — exactly 3 bullets — from pre-aggregated
stats (theme/sentiment/urgency counts, top duplicate clusters, contradictions),
never from raw feedback text. This keeps cost and latency bounded regardless
of how many thousands of rows are in the upload, and structurally prevents
the model from hallucinating numbers it was never shown.

Version: v1.0
Expected Output: {"signals": [{headline, detail, supporting_theme, severity_hint}, x3]}

Revision History
-----------------
- v1.0 (2026-07-21): initial version.
"""

from app.prompts._shared.canonical_themes import CANONICAL_THEMES
from app.prompts._shared.retry import STRICT_RETRY_REMINDER

PROMPT_VERSION = "v1.0"

REVISION_HISTORY = [
    {"version": "v1.0", "date": "2026-07-21", "change": "initial version", "author": "FeedbackIQ"},
]

SEVERITY_HINTS = ["info", "watch", "urgent"]

SYSTEM_PROMPT = f"""You are a product analytics summarizer for FeedbackIQ. You are given \
pre-computed aggregate statistics (NOT raw feedback text) for a batch of customer feedback: \
counts by theme, sentiment breakdown per theme, urgency distribution, top duplicate clusters, \
and confirmed contradictions. Produce EXACTLY three bullet "signals" — the most \
decision-relevant patterns a product manager should know. Do not invent numbers not present in \
the input aggregates — every figure you cite must come directly from the given stats.

Allowed themes for "supporting_theme": {CANONICAL_THEMES}

Output valid JSON only, matching the schema exactly, with no extra commentary."""

FEWSHOT_EXAMPLES = [
    {
        "input": {
            "theme_counts": {"Login & Authentication": 34, "Performance & Speed": 21, "Feature Request": 12},
            "sentiment_by_theme": {"Login & Authentication": {"Negative": 30, "Positive": 2, "Neutral": 2}},
            "top_duplicate_clusters": [
                {"theme": "Login & Authentication", "group_size": 12, "sample_text": "Unable to login to my account"}
            ],
            "contradictions": [{"theme": "UI/UX & Design", "count": 3}],
        },
        "output": {
            "signals": [
                {
                    "headline": "Login failures are this batch's dominant issue",
                    "detail": "34 items relate to Login & Authentication, 30 of them negative, including a 12-item duplicate cluster describing the same login failure.",
                    "supporting_theme": "Login & Authentication",
                    "severity_hint": "urgent",
                },
                {
                    "headline": "Performance complaints are the second-largest theme",
                    "detail": "21 items raised performance/speed concerns this batch.",
                    "supporting_theme": "Performance & Speed",
                    "severity_hint": "watch",
                },
                {
                    "headline": "Customers disagree on the new UI/UX changes",
                    "detail": "3 contradiction pairs were found on UI/UX & Design, indicating a split reaction to a recent change.",
                    "supporting_theme": "UI/UX & Design",
                    "severity_hint": "watch",
                },
            ]
        },
    }
]

JSON_SCHEMA = {
    "name": "key_signals_summary",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "signals": {
                "type": "array",
                "minItems": 3,
                "maxItems": 3,
                "items": {
                    "type": "object",
                    "properties": {
                        "headline": {"type": "string", "maxLength": 100},
                        "detail": {"type": "string", "maxLength": 250},
                        "supporting_theme": {"type": "string", "enum": CANONICAL_THEMES},
                        "severity_hint": {"type": "string", "enum": SEVERITY_HINTS},
                    },
                    "required": ["headline", "detail", "supporting_theme", "severity_hint"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["signals"],
        "additionalProperties": False,
    },
}


def build_messages(aggregate_stats: dict, *, is_retry: bool = False) -> list[dict]:
    system = SYSTEM_PROMPT
    if is_retry:
        system += STRICT_RETRY_REMINDER

    messages: list[dict] = [{"role": "system", "content": system}]
    for ex in FEWSHOT_EXAMPLES:
        messages.append({"role": "user", "content": f"Summarize: {ex['input']}"})
        messages.append({"role": "assistant", "content": str(ex["output"])})
    messages.append({"role": "user", "content": f"Summarize: {aggregate_stats}"})
    return messages
