"""Stage 1 (Reading File) and Stage 2 (Cleaning Data) helpers, shared by the
CSV and paste ingestion paths."""

import csv
import io
import re

MAX_CSV_SIZE_BYTES = 5 * 1024 * 1024
MIN_TEXT_LENGTH = 1
MAX_TEXT_LENGTH = 5000

_CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_WHITESPACE_RE = re.compile(r"\s+")


class InvalidCSVError(Exception):
    pass


def clean_text(raw_text: str) -> str | None:
    """Returns cleaned text, or None if the row should be dropped (empty/garbage)."""
    text = _CONTROL_CHARS_RE.sub("", raw_text)
    text = _WHITESPACE_RE.sub(" ", text).strip()
    if len(text) < MIN_TEXT_LENGTH:
        return None
    if len(text) > MAX_TEXT_LENGTH:
        text = text[:MAX_TEXT_LENGTH]
    return text


def parse_csv(file_bytes: bytes) -> list[str]:
    """Extracts feedback text from a CSV. Expects a 'feedback' column (case-insensitive);
    falls back to the first column if no such header exists."""
    if len(file_bytes) > MAX_CSV_SIZE_BYTES:
        raise InvalidCSVError("File exceeds the 5MB size limit.")
    if not file_bytes.strip():
        raise InvalidCSVError("The uploaded file is empty.")

    try:
        text = file_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        try:
            text = file_bytes.decode("latin-1")
        except UnicodeDecodeError as exc:
            raise InvalidCSVError("Could not decode file — please upload a UTF-8 CSV.") from exc

    try:
        reader = csv.DictReader(io.StringIO(text))
        if reader.fieldnames is None:
            raise InvalidCSVError("CSV has no header row.")
        feedback_col = next(
            (f for f in reader.fieldnames if f.strip().lower() == "feedback"), None
        )
        if feedback_col is None:
            feedback_col = reader.fieldnames[0]

        rows = []
        for row in reader:
            value = (row.get(feedback_col) or "").strip()
            if value:
                rows.append(value)
    except csv.Error as exc:
        raise InvalidCSVError(f"Could not parse CSV: {exc}") from exc

    if not rows:
        raise InvalidCSVError(f"No feedback text found in column '{feedback_col}'.")
    return rows
