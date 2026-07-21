"""
Thin OpenAI client wrapper: loads prompt modules, issues structured-output
calls, and applies the shared retry/fallback pattern from prompts/_shared/retry.py.

This is the one place that talks to OpenAI — pipeline_service and the
dedup/contradiction/summary/nlquery services all go through here, never
call the SDK directly. Keeping this isolated is what makes prompt versioning
and the eval harness able to swap models/prompts without touching callers.
"""

import difflib
import logging
import time

from openai import OpenAI

from app.core.config import get_settings
from app.prompts import classifier_prompt, duplicate_confirm_prompt, nlquery_prompt, split_prompt, summary_prompt
from app.prompts._shared.canonical_themes import CANONICAL_THEMES
from app.prompts._shared.retry import call_with_retry
from app.prompts._shared.schemas import (
    ClassificationBatchResult,
    ClassificationResult,
    DuplicateConfirmBatchResult,
    KeySignalsResult,
    NLQueryFilter,
    SplitResult,
)

logger = logging.getLogger(__name__)
settings = get_settings()
_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=settings.openai_api_key)
    return _client


def _fallback_classification(item_id: str) -> ClassificationResult:
    return ClassificationResult(
        id=item_id,
        category="Other",
        sentiment="Neutral",
        emotion="Neutral",
        urgency="Medium",
        severity="Minor",
        business_impact="None",
        intent="Other",
        theme="Other",
        confidence=0,
        explanation="AI processing failed after 2 attempts; flagged for manual review.",
        suggested_action="Review manually.",
        needs_human_review=True,
    )


def classify_batch(items: list[dict]) -> list[tuple[ClassificationResult, int, str]]:
    """
    items: [{"id": str, "text": str}, ...], length <= classifier_prompt.BATCH_SIZE.
    Returns [(ClassificationResult, processing_time_ms, raw_json_or_None), ...] in input order.
    """
    started = time.perf_counter()

    def call_fn(is_retry: bool) -> str:
        messages = classifier_prompt.build_messages(items, is_retry=is_retry)
        response = _get_client().chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            response_format={"type": "json_schema", "json_schema": classifier_prompt.JSON_SCHEMA},
        )
        return response.choices[0].message.content

    def parse_and_validate(raw: str) -> ClassificationBatchResult:
        parsed = ClassificationBatchResult.model_validate_json(raw)
        if len(parsed.results) != len(items):
            raise ValueError(
                f"expected {len(items)} results, got {len(parsed.results)}"
            )
        for result in parsed.results:
            violations = result.validate_enums()
            if violations:
                raise ValueError(f"enum violations for {result.id}: {violations}")
        return parsed

    result, attempts, raw_failed = call_with_retry(
        call_fn=call_fn,
        parse_and_validate=parse_and_validate,
        context_label=f"classify_batch[{len(items)} items]",
    )
    elapsed_ms = int((time.perf_counter() - started) * 1000)
    per_item_ms = max(elapsed_ms // max(len(items), 1), 1)

    if result is None:
        logger.error("classify_batch failed after %s attempts: %s", attempts, raw_failed)
        return [(_fallback_classification(item["id"]), per_item_ms, raw_failed) for item in items]

    by_id = {r.id: r for r in result.results}
    return [
        (by_id.get(item["id"], _fallback_classification(item["id"])), per_item_ms, None)
        for item in items
    ]


def split_feedback_blob(raw_blob: str) -> list[str]:
    """Splits a pasted multi-feedback blob into individual verbatim items."""

    def call_fn(is_retry: bool) -> str:
        messages = split_prompt.build_messages(raw_blob, is_retry=is_retry)
        response = _get_client().chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            response_format={"type": "json_schema", "json_schema": split_prompt.JSON_SCHEMA},
        )
        return response.choices[0].message.content

    def parse_and_validate(raw: str) -> SplitResult:
        parsed = SplitResult.model_validate_json(raw)
        if not parsed.items:
            raise ValueError("split returned zero items")
        for split_item in parsed.items:
            # containment guardrail: reject fabricated text not actually present in the blob
            ratio = difflib.SequenceMatcher(
                None, split_item.text.lower(), raw_blob.lower()
            ).find_longest_match(0, len(split_item.text), 0, len(raw_blob)).size
            if ratio < len(split_item.text) * 0.7:
                raise ValueError(f"split item not substantially contained in source: {split_item.text[:40]!r}")
        return parsed

    result, attempts, raw_failed = call_with_retry(
        call_fn=call_fn,
        parse_and_validate=parse_and_validate,
        context_label="split_feedback_blob",
    )
    if result is None:
        logger.warning(
            "split_feedback_blob failed after %s attempts, falling back to single item", attempts
        )
        return [raw_blob.strip()]
    return [item.text for item in result.items]


def confirm_duplicates(pairs: list[dict]) -> dict[str, tuple[bool, int, str]]:
    """
    pairs: [{"pair_id", "item_a_id", "item_b_id", "item_a", "item_b"}, ...]
    Returns {pair_id: (is_duplicate, confidence, reasoning)}. On failure, every pair
    defaults to (False, 0, "...") — safe default is "don't merge automatically."
    """
    if not pairs:
        return {}

    def call_fn(is_retry: bool) -> str:
        messages = duplicate_confirm_prompt.build_messages(pairs, is_retry=is_retry)
        response = _get_client().chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            response_format={
                "type": "json_schema",
                "json_schema": duplicate_confirm_prompt.JSON_SCHEMA,
            },
        )
        return response.choices[0].message.content

    def parse_and_validate(raw: str) -> DuplicateConfirmBatchResult:
        parsed = DuplicateConfirmBatchResult.model_validate_json(raw)
        if len(parsed.results) != len(pairs):
            raise ValueError(f"expected {len(pairs)} results, got {len(parsed.results)}")
        return parsed

    result, attempts, raw_failed = call_with_retry(
        call_fn=call_fn,
        parse_and_validate=parse_and_validate,
        context_label=f"confirm_duplicates[{len(pairs)} pairs]",
    )
    if result is None:
        logger.warning("confirm_duplicates failed after %s attempts: %s", attempts, raw_failed)
        return {p["pair_id"]: (False, 0, "AI confirmation failed; not auto-merged.") for p in pairs}

    return {r.pair_id: (r.is_duplicate, r.confidence, r.reasoning) for r in result.results}


def _fallback_signals(aggregate_stats: dict) -> list[dict]:
    """Code-generated template bullets — guarantees the dashboard never shows a broken summary."""
    theme_counts = aggregate_stats.get("theme_counts", {}) or {"Other": 0}
    top_themes = sorted(theme_counts.items(), key=lambda kv: kv[1], reverse=True)[:3]
    signals = []
    for theme, count in top_themes:
        sentiment_by_theme = aggregate_stats.get("sentiment_by_theme", {}).get(theme, {})
        negative = sentiment_by_theme.get("Negative", 0)
        pct = round((negative / count) * 100) if count else 0
        signals.append(
            {
                "headline": f"Top theme this batch: {theme}",
                "detail": f"{count} items, {pct}% negative.",
                "supporting_theme": theme if theme in CANONICAL_THEMES else "Other",
                "severity_hint": "watch" if pct >= 50 else "info",
            }
        )
    while len(signals) < 3:
        signals.append(
            {
                "headline": "No further signals this batch",
                "detail": "Not enough distinct themes in this batch to generate a third signal.",
                "supporting_theme": "Other",
                "severity_hint": "info",
            }
        )
    return signals[:3]


def generate_key_signals(aggregate_stats: dict) -> list[dict]:
    def call_fn(is_retry: bool) -> str:
        messages = summary_prompt.build_messages(aggregate_stats, is_retry=is_retry)
        response = _get_client().chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            response_format={"type": "json_schema", "json_schema": summary_prompt.JSON_SCHEMA},
        )
        return response.choices[0].message.content

    def parse_and_validate(raw: str) -> KeySignalsResult:
        return KeySignalsResult.model_validate_json(raw)

    result, attempts, raw_failed = call_with_retry(
        call_fn=call_fn,
        parse_and_validate=parse_and_validate,
        context_label="generate_key_signals",
    )
    if result is None:
        logger.warning("generate_key_signals failed after %s attempts: %s", attempts, raw_failed)
        return _fallback_signals(aggregate_stats)
    return [s.model_dump() for s in result.signals]


def translate_nl_query(query: str, *, today_iso: str) -> NLQueryFilter:
    def call_fn(is_retry: bool) -> str:
        messages = nlquery_prompt.build_messages(query, today_iso=today_iso, is_retry=is_retry)
        response = _get_client().chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            response_format={"type": "json_schema", "json_schema": nlquery_prompt.JSON_SCHEMA},
        )
        return response.choices[0].message.content

    def parse_and_validate(raw: str) -> NLQueryFilter:
        return NLQueryFilter.model_validate_json(raw)

    result, attempts, raw_failed = call_with_retry(
        call_fn=call_fn,
        parse_and_validate=parse_and_validate,
        context_label="translate_nl_query",
    )
    if result is None:
        logger.warning("translate_nl_query failed after %s attempts: %s", attempts, raw_failed)
        return NLQueryFilter()  # empty filter = show everything, per the fallback design
    return result
