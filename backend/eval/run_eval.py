"""
Evaluation harness for classifier_prompt.

Runs the hand-labeled eval_dataset.json through the live classifier and
computes per-field accuracy, confidence calibration, and processing time.
Writes one JSON + Markdown report per run, named with the prompt version so
version bumps produce a visible before/after diff instead of overwriting the
previous baseline.

Usage (from backend/, with the venv active and OPENAI_API_KEY set):
    python eval/run_eval.py
"""

import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.prompts import classifier_prompt  # noqa: E402
from app.services import ai_service  # noqa: E402

EVAL_DIR = Path(__file__).resolve().parent
DATASET_PATH = EVAL_DIR / "eval_dataset.json"
REPORTS_DIR = EVAL_DIR / "reports"

FIELDS = ["category", "sentiment", "theme", "urgency", "emotion"]


def chunked(seq: list, size: int) -> list[list]:
    return [seq[i : i + size] for i in range(0, len(seq), size)]


def run() -> dict:
    dataset = json.loads(DATASET_PATH.read_text())
    items = dataset["items"]

    predictions: dict[str, tuple] = {}
    for batch in chunked(items, classifier_prompt.BATCH_SIZE):
        call_items = [{"id": item["id"], "text": item["text"]} for item in batch]
        results = ai_service.classify_batch(call_items)
        for item, (result, processing_ms, raw_failed) in zip(batch, results):
            predictions[item["id"]] = (result, processing_ms, raw_failed)

    field_correct = {f: 0 for f in FIELDS}
    field_total = {f: 0 for f in FIELDS}
    confidences: list[int] = []
    processing_times: list[int] = []
    fallback_count = 0
    per_item_rows = []

    for item in items:
        result, processing_ms, raw_failed = predictions[item["id"]]
        confidences.append(result.confidence)
        processing_times.append(processing_ms)
        if raw_failed is not None:
            fallback_count += 1

        row = {"id": item["id"], "hard_case_type": item["hard_case_type"]}
        for field in FIELDS:
            gold_key = f"gold_{field}"
            predicted_value = getattr(result, field)
            gold_value = item[gold_key]
            is_correct = predicted_value == gold_value
            field_total[field] += 1
            field_correct[field] += int(is_correct)
            row[field] = {"predicted": predicted_value, "gold": gold_value, "correct": is_correct}
        row["confidence"] = result.confidence
        row["needs_human_review"] = result.needs_human_review
        per_item_rows.append(row)

    accuracy = {f: round(field_correct[f] / field_total[f], 3) for f in FIELDS}
    avg_confidence = round(sum(confidences) / len(confidences), 1)
    avg_processing_ms = round(sum(processing_times) / len(processing_times), 1)

    # Confidence calibration: are low-confidence items actually the ones the model got wrong?
    correct_confidences = [
        row["confidence"] for row in per_item_rows if all(row[f]["correct"] for f in FIELDS)
    ]
    incorrect_confidences = [
        row["confidence"] for row in per_item_rows if not all(row[f]["correct"] for f in FIELDS)
    ]
    avg_conf_when_correct = round(sum(correct_confidences) / len(correct_confidences), 1) if correct_confidences else None
    avg_conf_when_incorrect = round(sum(incorrect_confidences) / len(incorrect_confidences), 1) if incorrect_confidences else None

    report = {
        "prompt_version": classifier_prompt.PROMPT_VERSION,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "dataset_size": len(items),
        "field_accuracy": accuracy,
        "overall_exact_match_accuracy": round(
            sum(1 for row in per_item_rows if all(row[f]["correct"] for f in FIELDS)) / len(items), 3
        ),
        "avg_confidence": avg_confidence,
        "avg_confidence_when_all_fields_correct": avg_conf_when_correct,
        "avg_confidence_when_any_field_wrong": avg_conf_when_incorrect,
        "avg_processing_time_ms": avg_processing_ms,
        "fallback_rate": round(fallback_count / len(items), 3),
        "per_item": per_item_rows,
    }
    return report


def render_markdown(report: dict) -> str:
    lines = [
        f"# Eval Report — classifier_prompt {report['prompt_version']}",
        "",
        f"Generated: {report['generated_at']}",
        f"Dataset size: {report['dataset_size']} items",
        "",
        "## Field Accuracy",
        "",
        "| Field | Accuracy |",
        "|---|---|",
    ]
    for field, acc in report["field_accuracy"].items():
        lines.append(f"| {field} | {acc * 100:.1f}% |")
    lines += [
        "",
        f"**Overall exact-match accuracy (all 5 fields correct): {report['overall_exact_match_accuracy'] * 100:.1f}%**",
        "",
        "## Confidence Calibration",
        "",
        f"- Average confidence: {report['avg_confidence']}",
        f"- Average confidence when fully correct: {report['avg_confidence_when_all_fields_correct']}",
        f"- Average confidence when any field wrong: {report['avg_confidence_when_any_field_wrong']}",
        "",
        "(A well-calibrated model shows a meaningfully lower average confidence on the "
        "incorrect group — that gap is what makes the `needs_human_review` flag useful "
        "rather than decorative.)",
        "",
        "## Performance",
        "",
        f"- Average processing time per item: {report['avg_processing_time_ms']} ms",
        f"- Fallback rate (both attempts failed validation): {report['fallback_rate'] * 100:.1f}%",
        "",
        "## Per-Item Breakdown",
        "",
        "| ID | Type | Category | Sentiment | Theme | Urgency | Emotion | Confidence |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in report["per_item"]:
        def mark(field):
            return "✅" if row[field]["correct"] else f"❌ (got {row[field]['predicted']}, want {row[field]['gold']})"

        lines.append(
            f"| {row['id']} | {row['hard_case_type']} | {mark('category')} | {mark('sentiment')} "
            f"| {mark('theme')} | {mark('urgency')} | {mark('emotion')} | {row['confidence']} |"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    report = run()
    REPORTS_DIR.mkdir(exist_ok=True)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    json_path = REPORTS_DIR / f"eval_report_{report['prompt_version']}_{stamp}.json"
    md_path = REPORTS_DIR / f"eval_report_{report['prompt_version']}_{stamp}.md"
    json_path.write_text(json.dumps(report, indent=2))
    md_path.write_text(render_markdown(report))
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    print()
    print(f"Field accuracy: {report['field_accuracy']}")
    print(f"Overall exact-match accuracy: {report['overall_exact_match_accuracy']}")
    print(f"Avg confidence (correct vs incorrect): {report['avg_confidence_when_all_fields_correct']} vs {report['avg_confidence_when_any_field_wrong']}")
