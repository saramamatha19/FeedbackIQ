"""
duplicate_confirm_prompt.py

Purpose
-------
Confirms whether a shortlisted candidate pair describes the SAME underlying
complaint (a true duplicate a support agent would file under one ticket), not
just lexically similar text. Only ever called on pairs that already passed a
non-LLM fuzzy pre-filter (rapidfuzz token_sort_ratio >= 70, within the same
theme) — see duplicate_service.py. This keeps LLM calls bounded to a small
shortlist instead of every pair in a batch, and keeps the job narrow/auditable.

Version: v1.0
Expected Output: {"results": [{pair_id, item_a_id, item_b_id, is_duplicate, confidence, reasoning}, ...]}

Revision History
-----------------
- v1.0 (2026-07-21): initial version.
"""

from app.prompts._shared.retry import STRICT_RETRY_REMINDER

PROMPT_VERSION = "v1.0"
BATCH_SIZE = 15

REVISION_HISTORY = [
    {"version": "v1.0", "date": "2026-07-21", "change": "initial version", "author": "FeedbackIQ"},
]

SYSTEM_PROMPT = """You are checking whether two pieces of customer feedback describe the SAME \
underlying issue or complaint (a true duplicate), as opposed to two different problems that \
merely share topic/theme or wording. Two items are duplicates only if a support agent would \
file them under the exact same ticket. Similar wording is NOT sufficient on its own; different \
wording describing the same root cause IS sufficient. Return is_duplicate=false if they share a \
theme but differ in the specific problem.

Output valid JSON only, matching the schema exactly, with no extra commentary. Return exactly \
one result per input pair, carrying its "pair_id" unchanged."""

FEWSHOT_EXAMPLES = [
    {
        "input": {
            "pair_id": "ex1", "item_a_id": "a", "item_b_id": "b",
            "item_a": "Unable to login to my account since yesterday",
            "item_b": "Can't sign in, keeps saying wrong password even though it's correct",
        },
        "output": {
            "pair_id": "ex1", "item_a_id": "a", "item_b_id": "b",
            "is_duplicate": True, "confidence": 88,
            "reasoning": "Both describe an inability to authenticate/sign in; different phrasing but same root complaint (login failure).",
        },
    },
    {
        "input": {
            "pair_id": "ex2", "item_a_id": "a", "item_b_id": "b",
            "item_a": "Login page takes forever to load",
            "item_b": "Login button doesn't work when I click it, nothing happens",
        },
        "output": {
            "pair_id": "ex2", "item_a_id": "a", "item_b_id": "b",
            "is_duplicate": False, "confidence": 80,
            "reasoning": "Both are login-related but describe different problems: one is a slow-loading page (performance), the other is a non-functional button (broken action) — same theme, different root cause.",
        },
    },
    {
        "input": {
            "pair_id": "ex3", "item_a_id": "a", "item_b_id": "b",
            "item_a": "app crashes every time i open reports",
            "item_b": "Reports section crashes the app every single time",
        },
        "output": {
            "pair_id": "ex3", "item_a_id": "a", "item_b_id": "b",
            "is_duplicate": True, "confidence": 95,
            "reasoning": "Nearly identical restatement of the same crash in the reports section.",
        },
    },
]

JSON_SCHEMA = {
    "name": "duplicate_confirmation_batch",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "results": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "pair_id": {"type": "string"},
                        "item_a_id": {"type": "string"},
                        "item_b_id": {"type": "string"},
                        "is_duplicate": {"type": "boolean"},
                        "confidence": {"type": "integer", "minimum": 0, "maximum": 100},
                        "reasoning": {"type": "string", "maxLength": 200},
                    },
                    "required": ["pair_id", "item_a_id", "item_b_id", "is_duplicate", "confidence", "reasoning"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["results"],
        "additionalProperties": False,
    },
}


def build_messages(pairs: list[dict], *, is_retry: bool = False) -> list[dict]:
    """pairs: [{"pair_id", "item_a_id", "item_b_id", "item_a", "item_b"}, ...]"""
    system = SYSTEM_PROMPT
    if is_retry:
        system += STRICT_RETRY_REMINDER

    messages: list[dict] = [{"role": "system", "content": system}]
    for ex in FEWSHOT_EXAMPLES:
        messages.append({"role": "user", "content": f"Compare: {ex['input']}"})
        messages.append({"role": "assistant", "content": str({"results": [ex["output"]]})})
    messages.append({"role": "user", "content": f"Compare each of the following {len(pairs)} pair(s): {pairs}"})
    return messages


'''Different customers can describe the same issue using different words. 
The duplicate confirmation prompt determines whether two feedback items refer 
to the same underlying problem so the dashboard can group them together.'''