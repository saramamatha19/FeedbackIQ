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

Version: v1.1
Expected Output: {"items": [{"text": str, "detected_separator_style": str}, ...]}

Revision History
-----------------
- v1.0 (2026-07-21): initial version.
- v1.1 (2026-07-22): topic-shift detection was keyed to connector words ("also,",
  "another thing,"), and the "return SINGLE item if unsure" escape hatch let the
  model default to one item for any run-on paragraph without those exact phrases —
  a real multi-complaint paragraph with plain sentences (no connector words) came
  back as a single item. Rewrote to split by topic/subject change per sentence or
  clause regardless of connector wording, and restricted the single-item case to
  text that is genuinely about one topic throughout.
"""

SPLIT_RETRY_REMINDER = (
    "\n\nYour previous response was invalid — either it wasn't valid JSON matching the schema, "
    "or one of the returned \"text\" values wasn't a verbatim substring of the original input "
    "(only whitespace normalization is allowed; never paraphrase or summarize). Re-split the "
    "text: identify each distinct topic (a specific bug, feature request, praise, or complaint) "
    "as its own item, copying the exact original wording for each, and return valid JSON only."
)

PROMPT_VERSION = "v1.1"

REVISION_HISTORY = [
    {"version": "v1.0", "date": "2026-07-21", "change": "initial version", "author": "FeedbackIQ"},
    {
        "version": "v1.1",
        "date": "2026-07-22",
        "change": "split by topic/subject change instead of connector words; narrowed the single-item fallback",
        "author": "FeedbackIQ",
    },
]

SEPARATOR_STYLES = ["bullet", "numbered", "blank_line", "single_item", "paragraph_heuristic"]

SYSTEM_PROMPT = """You split raw pasted customer feedback text into individual, standalone \
feedback items — one item per distinct topic (a specific bug, feature request, piece of \
praise, question, or complaint about a specific thing). Preserve original wording VERBATIM \
(do not summarize, paraphrase, or edit); every output "text" value must be a verbatim substring \
(allowing only whitespace normalization) of the input — never invent content that wasn't there.

First, detect structural separators: bullets (-, *, •), numbered lists (1., 2)), or blank-line- \
separated paragraphs — split on those directly.

If none of those patterns exist and the text reads as one continuous paragraph, split by TOPIC, \
not by connector words: a new sentence or clause that names a different feature, bug, \
interaction, or request is a new item — whether or not it's introduced by a transition phrase \
("also", "another thing"). Plain conjunctions ("and", "however", "on the positive side", "one \
more thing", "overall"), or no connector at all, are just as much a boundary as an explicit \
transition phrase. Only keep consecutive sentences in the same item when they continue \
describing the SAME specific issue (e.g. a symptom followed by more detail about that same \
symptom).

Only return a SINGLE item when the entire text is genuinely about one topic/interaction from \
start to finish. The absence of an explicit transition word is NOT by itself a reason to keep \
text together — a paragraph mentioning several different features, bugs, or requests must be \
split into that many items even when written as one run-on passage with commas and "and"s.

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
    {
        # No bullets/numbers/blank lines AND no connector phrases like "also," or "another
        # thing," — each sentence is its own topic and must still be split accordingly.
        "input": "The checkout button is unresponsive on mobile Safari, though it works fine on desktop. Your support agent Maria was incredibly patient and fixed my refund issue in minutes. Load times on the reports page have gotten noticeably worse this month. It would help a lot if the app supported multiple currencies. I think the free trial should be longer than 7 days.",
        "output": {
            "items": [
                {"text": "The checkout button is unresponsive on mobile Safari, though it works fine on desktop.", "detected_separator_style": "paragraph_heuristic"},
                {"text": "Your support agent Maria was incredibly patient and fixed my refund issue in minutes.", "detected_separator_style": "paragraph_heuristic"},
                {"text": "Load times on the reports page have gotten noticeably worse this month.", "detected_separator_style": "paragraph_heuristic"},
                {"text": "It would help a lot if the app supported multiple currencies.", "detected_separator_style": "paragraph_heuristic"},
                {"text": "I think the free trial should be longer than 7 days.", "detected_separator_style": "paragraph_heuristic"},
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
        system += SPLIT_RETRY_REMINDER

    messages: list[dict] = [{"role": "system", "content": system}]
    for ex in FEWSHOT_EXAMPLES:
        messages.append({"role": "user", "content": f"Split: {ex['input']!r}"})
        messages.append({"role": "assistant", "content": str(ex["output"])})
    messages.append({"role": "user", "content": f"Split: {raw_blob!r}"})
    return messages
