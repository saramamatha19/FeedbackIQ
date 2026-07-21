"""
split_prompt.py

Purpose
-------
Takes one raw pasted blob (bullets, numbered list, blank-line-separated
paragraphs, or a single run-on paragraph) and splits it into discrete,
standalone feedback items, without altering the original wording.

This is a genuinely separate call from classifier_prompt because its I/O
shape is different (1 string in, N strings out) and it runs *before*
classification exists — there's nothing to fold it into.

Version: v1.0
Expected Output: {"items": [{"text": str, "detected_separator_style": str}, ...]}

Revision History
-----------------
- v1.0 (2026-07-21): initial version.
"""

from app.prompts._shared.retry import STRICT_RETRY_REMINDER

PROMPT_VERSION = "v1.0"

REVISION_HISTORY = [
    {"version": "v1.0", "date": "2026-07-21", "change": "initial version", "author": "FeedbackIQ"},
]

SEPARATOR_STYLES = ["bullet", "numbered", "blank_line", "single_item", "paragraph_heuristic"]

SYSTEM_PROMPT = """You split raw pasted customer feedback text into individual, standalone \
feedback items. Preserve original wording VERBATIM (do not summarize, paraphrase, or edit). \
Detect bullets (-, *, •), numbered lists (1., 2)), blank-line-separated paragraphs, or — if \
none of these patterns exist and the text reads as one continuous rambling comment — treat \
topic shifts (e.g. "also,", "another thing,", a new sentence starting a new complaint) as soft \
boundaries. If you cannot confidently separate a rambling paragraph into distinct complaints, \
return it as a SINGLE item rather than fabricating artificial splits. Never invent content that \
wasn't in the original text — every output "text" value must be a verbatim substring (allowing \
only whitespace normalization) of the input.

Output valid JSON only, matching the schema exactly, with no extra commentary."""

FEWSHOT_EXAMPLES = [
    {
        "input": "so I've been using this for like 3 months now and honestly the search feature never finds what I'm looking for, it's really annoying, and also can we PLEASE get dark mode already, every other app has it, oh and one more thing the mobile notifications are super delayed sometimes by hours which defeats the purpose",
        "output": {
            "items": [
                {"text": "the search feature never finds what I'm looking for, it's really annoying", "detected_separator_style": "paragraph_heuristic"},
                {"text": "can we PLEASE get dark mode already, every other app has it", "detected_separator_style": "paragraph_heuristic"},
                {"text": "the mobile notifications are super delayed sometimes by hours which defeats the purpose", "detected_separator_style": "paragraph_heuristic"},
            ]
        },
    },
    {
        "input": "great app, keep it up!",
        "output": {"items": [{"text": "great app, keep it up!", "detected_separator_style": "single_item"}]},
    },
    {
        "input": "1) crashes on startup sometimes\n2) love the new dashboard\n3) billing page shows wrong currency",
        "output": {
            "items": [
                {"text": "crashes on startup sometimes", "detected_separator_style": "numbered"},
                {"text": "love the new dashboard", "detected_separator_style": "numbered"},
                {"text": "billing page shows wrong currency", "detected_separator_style": "numbered"},
            ]
        },
    },
]

JSON_SCHEMA = {
    "name": "feedback_split",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                        "detected_separator_style": {"type": "string", "enum": SEPARATOR_STYLES},
                    },
                    "required": ["text", "detected_separator_style"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["items"],
        "additionalProperties": False,
    },
}


def build_messages(raw_blob: str, *, is_retry: bool = False) -> list[dict]:
    system = SYSTEM_PROMPT
    if is_retry:
        system += STRICT_RETRY_REMINDER

    messages: list[dict] = [{"role": "system", "content": system}]
    for ex in FEWSHOT_EXAMPLES:
        messages.append({"role": "user", "content": f"Split: {ex['input']!r}"})
        messages.append({"role": "assistant", "content": str(ex["output"])})
    messages.append({"role": "user", "content": f"Split: {raw_blob!r}"})
    return messages
