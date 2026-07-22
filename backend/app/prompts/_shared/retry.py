"""
Uniform retry/fallback wrapper used by every prompt module.

Pattern (identical across classifier/split/duplicate/contradiction/summary):
  attempt 1 -> parse + validate
  on failure -> attempt 2 with a stricter system reminder appended
  on second failure -> caller-supplied safe-default fallback, flagged for review

Low confidence alone is NEVER a reason to retry here — that's a valid model
signal (ambiguous/sarcastic/short input), not an error. Retries are reserved
strictly for format/parse/enum failures so we don't double API cost on every
merely-ambiguous item.
"""

import json
import logging
from collections.abc import Callable
from typing import TypeVar

from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

STRICT_RETRY_REMINDER = (
    "\n\nYour previous response was invalid. You MUST return a single JSON object "
    "that exactly matches the required schema, using ONLY the allowed enum values "
    "listed above, with no text outside the JSON object and no missing fields."
)


class PromptFailure(Exception):
    """Raised internally when both attempts fail; callers catch this and apply their fallback."""


def call_with_retry(
    *,
    call_fn: Callable[[bool], str],
    parse_and_validate: Callable[[str], T],
    context_label: str,
) -> tuple[T | None, int, str | None]:
    """
    call_fn(is_retry: bool) -> raw JSON string from the model.
    parse_and_validate(raw: str) -> parsed Pydantic model; must raise on invalid input.

    Returns (result_or_None, attempts_used, raw_failed_response_or_None).
    """
    raw: str | None = None
    for attempt, is_retry in enumerate((False, True), start=1):
        try:
            raw = call_fn(is_retry)
            result = parse_and_validate(raw)
            return result, attempt, None
        except (json.JSONDecodeError, ValidationError, ValueError) as exc:
            logger.warning(
                "%s: attempt %s failed validation (%s)", context_label, attempt, exc
            )
            continue
    return None, 2, raw
