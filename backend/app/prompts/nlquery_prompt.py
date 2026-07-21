"""
nlquery_prompt.py

Purpose
-------
Translates a user's natural-language search query into a structured filter —
never raw SQL. The LLM's output is validated against an enum-constrained
schema and then translated into a parameterized SQLAlchemy query by
nl_query_service.py, which enforces a field/operator allowlist server-side.
This is defense-in-depth: even if the model ignored every instruction here
and hallucinated arbitrary field names, the code-level allowlist in
nl_query_service.py is what actually prevents SQL injection / cross-tenant
leakage, not this prompt.

Version: v1.0
Expected Output: NLFilter (see _shared/schemas.py)

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

SENTIMENT_VALUES = ["Positive", "Negative", "Neutral", "Mixed"]
URGENCY_VALUES = ["Low", "Medium", "High", "Critical"]

SYSTEM_PROMPT = f"""Translate the user's natural-language request into a structured filter over \
a customer feedback database. Use ONLY the provided enum values for theme/sentiment/urgency — \
if the user mentions a topic that doesn't map cleanly onto one of the allowed themes, leave \
"themes" empty and put the raw term in "keyword" instead. NEVER invent a new theme, sentiment, \
or urgency value under any circumstance. Dates should be resolved relative to today's date, \
which will be given to you, and expressed as ISO YYYY-MM-DD.

Allowed themes: {CANONICAL_THEMES}
Allowed sentiments: {SENTIMENT_VALUES}
Allowed urgencies: {URGENCY_VALUES}

Output valid JSON only, matching the schema exactly, with no extra commentary."""

FEWSHOT_EXAMPLES = [
    {
        "input": {"query": "show me urgent login complaints from last week", "today": "2026-07-20"},
        "output": {
            "themes": ["Login & Authentication"], "sentiments": ["Negative"],
            "urgencies": ["High", "Critical"], "date_from": "2026-07-13", "date_to": "2026-07-20",
            "only_duplicates": False, "only_contradictions": False, "only_needs_review": False,
            "keyword": None,
        },
    },
    {
        "input": {"query": "what are people saying that contradicts each other about the new UI", "today": "2026-07-20"},
        "output": {
            "themes": ["UI/UX & Design"], "sentiments": [], "urgencies": [], "date_from": None,
            "date_to": None, "only_duplicates": False, "only_contradictions": True,
            "only_needs_review": False, "keyword": None,
        },
    },
    {
        "input": {"query": "positive feedback about our new referral program", "today": "2026-07-20"},
        "output": {
            "themes": [], "sentiments": ["Positive"], "urgencies": [], "date_from": None,
            "date_to": None, "only_duplicates": False, "only_contradictions": False,
            "only_needs_review": False, "keyword": "referral program",
        },
    },
]

JSON_SCHEMA = {
    "name": "nl_query_filter",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "themes": {"type": "array", "items": {"type": "string", "enum": CANONICAL_THEMES}},
            "sentiments": {"type": "array", "items": {"type": "string", "enum": SENTIMENT_VALUES}},
            "urgencies": {"type": "array", "items": {"type": "string", "enum": URGENCY_VALUES}},
            "date_from": {"type": ["string", "null"]},
            "date_to": {"type": ["string", "null"]},
            "only_duplicates": {"type": "boolean"},
            "only_contradictions": {"type": "boolean"},
            "only_needs_review": {"type": "boolean"},
            "keyword": {"type": ["string", "null"]},
        },
        "required": [
            "themes", "sentiments", "urgencies", "date_from", "date_to",
            "only_duplicates", "only_contradictions", "only_needs_review", "keyword",
        ],
        "additionalProperties": False,
    },
}


def build_messages(query: str, *, today_iso: str, is_retry: bool = False) -> list[dict]:
    system = SYSTEM_PROMPT
    if is_retry:
        system += STRICT_RETRY_REMINDER

    messages: list[dict] = [{"role": "system", "content": system}]
    for ex in FEWSHOT_EXAMPLES:
        messages.append({"role": "user", "content": f"Translate: {ex['input']}"})
        messages.append({"role": "assistant", "content": str(ex["output"])})
    messages.append({"role": "user", "content": f"Translate: {{'query': {query!r}, 'today': {today_iso!r}}}"})
    return messages
