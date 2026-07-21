"""
classifier_prompt.py

Purpose
-------
The workhorse of the AI pipeline. One structured-JSON call classifies a batch
of feedback items across every dimension that's a correlated read of the same
text: category, sentiment, emotion, urgency, severity, business impact,
intent, theme, confidence, explanation, and suggested action.

Why one mega-prompt instead of N separate calls per dimension: these fields
are not independent judgments requiring separate reasoning contexts — they're
all derived from the same read of the same text. Splitting them would multiply
fixed per-call overhead (system prompt + few-shot tokens + round trip) for
zero accuracy gain, which matters when batches run to thousands of rows.

Batching: up to BATCH_SIZE items go in one call, id-matched so the backend can
verify result count == input count and re-associate outputs with their source
feedback rows. This amortizes the ~900-1200 token fixed cost of the system
prompt + few-shots across many items instead of paying it once per item.

Version: v1.1
Expected Output: {"results": [ClassificationResult, ...]} — see _shared/schemas.py

Revision History
-----------------
- v1.0 (2026-07-21): initial version.
- v1.1 (2026-07-21): baseline eval (eval/reports/eval_report_v1.0_*) showed urgency
  was the weakest field (71% vs 84-97% for other fields), with the model routinely
  under-calling severe cases as "High" where the gold set expected "Critical" (app
  crashes with data loss, repeated login lockout). Added an explicit urgency
  decision rule tying "Critical" directly to the spec's own named examples (crash,
  data loss, payment failure, cannot login, account locked) and a new few-shot
  example demonstrating a crash+data-loss item classified Critical.
"""

from app.prompts._shared.canonical_themes import CANONICAL_THEMES
from app.prompts._shared.schemas import (
    BUSINESS_IMPACT_VALUES,
    CATEGORY_VALUES,
    EMOTION_VALUES,
    INTENT_VALUES,
    SENTIMENT_VALUES,
    SEVERITY_VALUES,
    URGENCY_VALUES,
)

PROMPT_VERSION = "v1.1"
BATCH_SIZE = 15

REVISION_HISTORY = [
    {"version": "v1.0", "date": "2026-07-21", "change": "initial version", "author": "FeedbackIQ"},
]

SYSTEM_PROMPT = f"""You are a senior product feedback analyst for FeedbackIQ. You will be given \
one or more pieces of raw, unfiltered customer feedback — each may contain typos, emoji, \
sarcasm, mixed languages, or be a single word. Classify EACH item strictly according to the \
schema below.

You MUST choose exactly one value from each allowed list — never invent a new category, \
theme, emotion, or label under any circumstance. If nothing fits well, choose "Other". If the \
text is ambiguous, sarcastic, or too short to be sure, LOWER your confidence score accordingly \
rather than guessing with false certainty.

Confidence rubric (apply literally):
- 90-100: explicit and unambiguous
- 60-89: clear with minor inference required
- 30-59: ambiguous, sarcastic, vague, or very short
- 0-29: effectively uninterpretable

Urgency decision rule (apply literally, do not soften): if the feedback describes any of these
— app crash, data loss, payment failure, complete inability to log in, or an account lockout —
classify urgency as "Critical", not "High", UNLESS the text itself signals the impact was minor
or already resolved (e.g. "briefly", "but it fixed itself", "on my old account which I don't use").
Repeated/recurring occurrences of an issue (e.g. "third time this week", "every single time")
push severity and urgency up, not down. Reserve "High" for issues that are serious and
time-sensitive but do not meet the Critical bar above (e.g. a slow-loading page, a confusing
billing page, a delayed but eventually-delivered notification).

Base every judgment ONLY on the text given — do not assume context you don't have. If a single \
item raises multiple distinct issues, choose the single most dominant/actionable one as the \
primary classification, and mention the other issue(s) briefly in the explanation, and set \
needs_human_review to true.

Allowed values:
- category: {CATEGORY_VALUES}
- sentiment: {SENTIMENT_VALUES}
- emotion: {EMOTION_VALUES}
- urgency: {URGENCY_VALUES}
- severity: {SEVERITY_VALUES}
- business_impact: {BUSINESS_IMPACT_VALUES}
- intent: {INTENT_VALUES}
- theme: {CANONICAL_THEMES}

Output valid JSON only, matching the schema exactly, with no extra commentary outside the JSON \
object. Return exactly one result per input item, in the same order, each carrying the input's \
"id" field unchanged."""

FEWSHOT_EXAMPLES = [
    {
        "input": {"id": "ex1", "text": "Oh great, ANOTHER update that breaks the export button. Love it. 10/10 no notes."},
        "output": {
            "id": "ex1",
            "category": "Bug",
            "sentiment": "Negative",
            "emotion": "Frustration",
            "urgency": "Medium",
            "severity": "Moderate",
            "business_impact": "Medium",
            "intent": "Report Issue",
            "theme": "Data Export/Import",
            "confidence": 78,
            "explanation": "Sarcastic praise ('love it', '10/10') paired with a stated bug (export button broken after update) indicates negative sentiment expressed ironically.",
            "suggested_action": "Investigate export button regression from latest release.",
            "needs_human_review": False,
        },
    },
    {
        "input": {"id": "ex2", "text": "Bad."},
        "output": {
            "id": "ex2",
            "category": "Complaint",
            "sentiment": "Negative",
            "emotion": "Disappointment",
            "urgency": "Low",
            "severity": "Minor",
            "business_impact": "None",
            "intent": "Express Opinion",
            "theme": "Other",
            "confidence": 35,
            "explanation": "Single-word negative sentiment with no specific detail; cannot determine which product area is affected.",
            "suggested_action": "Follow up with user to get specifics before acting.",
            "needs_human_review": True,
        },
    },
    {
        "input": {"id": "ex3", "text": "app bahut slow ho gaya hai after the update 😤😤 please fix asap!!"},
        "output": {
            "id": "ex3",
            "category": "Bug",
            "sentiment": "Negative",
            "emotion": "Frustration",
            "urgency": "High",
            "severity": "Major",
            "business_impact": "High",
            "intent": "Report Issue",
            "theme": "Performance & Speed",
            "confidence": 85,
            "explanation": "Hindi-English code-switched text clearly states the app became slow after an update; angry emoji and 'asap' signal high urgency.",
            "suggested_action": "Prioritize investigation of performance regression from the latest release.",
            "needs_human_review": False,
        },
    },
    {
        "input": {
            "id": "ex4",
            "text": "Login keeps failing on mobile, also your support team took 5 days to reply, and honestly the pricing page is confusing too.",
        },
        "output": {
            "id": "ex4",
            "category": "Bug",
            "sentiment": "Negative",
            "emotion": "Frustration",
            "urgency": "High",
            "severity": "Major",
            "business_impact": "High",
            "intent": "Report Issue",
            "theme": "Login & Authentication",
            "confidence": 65,
            "explanation": "Three distinct issues raised (login failure, slow support response, confusing pricing); login failure chosen as primary theme since it is the functional blocker, but this item mixes multiple concerns and may warrant splitting for separate tracking.",
            "suggested_action": "Fix mobile login failure; separately review support SLA and pricing page clarity.",
            "needs_human_review": True,
        },
    },
    {
        "input": {
            "id": "ex_urgency",
            "text": "App crashed again while exporting my invoice. Lost all my unsaved changes for the third time this week.",
        },
        "output": {
            "id": "ex_urgency",
            "category": "Bug",
            "sentiment": "Negative",
            "emotion": "Anger",
            "urgency": "Critical",
            "severity": "Blocker",
            "business_impact": "High",
            "intent": "Report Issue",
            "theme": "Reliability & Bugs",
            "confidence": 90,
            "explanation": "Explicit crash with data loss, and it has recurred three times this week — meets the Critical bar per the urgency decision rule regardless of the crash itself being 'just' a crash.",
            "suggested_action": "Escalate to engineering immediately — recurring crash with confirmed data loss.",
            "needs_human_review": False,
        },
    },
    {
        "input": {"id": "ex5", "text": "It's fine I guess."},
        "output": {
            "id": "ex5",
            "category": "Other",
            "sentiment": "Neutral",
            "emotion": "Neutral",
            "urgency": "Low",
            "severity": "Minor",
            "business_impact": "None",
            "intent": "Express Opinion",
            "theme": "Other",
            "confidence": 25,
            "explanation": "Extremely vague, non-committal statement gives no actionable signal or specific topic.",
            "suggested_action": "No action; consider prompting user for more detail if collected via a follow-up survey.",
            "needs_human_review": True,
        },
    },
]

JSON_SCHEMA = {
    "name": "classification_batch",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "results": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "category": {"type": "string", "enum": CATEGORY_VALUES},
                        "sentiment": {"type": "string", "enum": SENTIMENT_VALUES},
                        "emotion": {"type": "string", "enum": EMOTION_VALUES},
                        "urgency": {"type": "string", "enum": URGENCY_VALUES},
                        "severity": {"type": "string", "enum": SEVERITY_VALUES},
                        "business_impact": {"type": "string", "enum": BUSINESS_IMPACT_VALUES},
                        "intent": {"type": "string", "enum": INTENT_VALUES},
                        "theme": {"type": "string", "enum": CANONICAL_THEMES},
                        "confidence": {"type": "integer", "minimum": 0, "maximum": 100},
                        "explanation": {"type": "string", "maxLength": 300},
                        "suggested_action": {"type": "string", "maxLength": 200},
                        "needs_human_review": {"type": "boolean"},
                    },
                    "required": [
                        "id", "category", "sentiment", "emotion", "urgency", "severity",
                        "business_impact", "intent", "theme", "confidence", "explanation",
                        "suggested_action", "needs_human_review",
                    ],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["results"],
        "additionalProperties": False,
    },
}


def build_messages(items: list[dict], *, is_retry: bool = False) -> list[dict]:
    """items: [{"id": str, "text": str}, ...] — at most BATCH_SIZE per call."""
    system = SYSTEM_PROMPT
    if is_retry:
        from app.prompts._shared.retry import STRICT_RETRY_REMINDER

        system += STRICT_RETRY_REMINDER

    messages: list[dict] = [{"role": "system", "content": system}]
    for ex in FEWSHOT_EXAMPLES:
        messages.append({"role": "user", "content": f"Classify: {ex['input']}"})
        messages.append({"role": "assistant", "content": str({"results": [ex["output"]]})})
    messages.append(
        {"role": "user", "content": f"Classify each of the following {len(items)} item(s): {items}"}
    )
    return messages
