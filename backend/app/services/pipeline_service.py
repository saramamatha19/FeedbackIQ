"""
Orchestrates the 8-stage ingestion pipeline for paste/CSV uploads:
Reading File -> Cleaning Data -> Removing Duplicates -> Running AI ->
Extracting Themes -> Generating Summary -> Saving Database -> Dashboard Ready.

Runs as a FastAPI BackgroundTasks job (see api/v1/endpoints/uploads.py) with
its own DB session — background tasks outlive the request that scheduled
them, so they cannot reuse the request-scoped session.

"Reading File" happens synchronously in the endpoint before this is
scheduled (fast: just parsing + row inserts) so the client gets an
upload_id immediately; this module picks up from "Cleaning Data" onward.

"Removing Duplicates" here is the cheap, non-LLM exact-match pass (collapse
literal repeats before spending AI classification cost on them) — the
semantic, theme-aware fuzzy+LLM dedup runs later, folded into "Extracting
Themes" since it genuinely needs the themes classification just produced.
"""

import logging
import uuid

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models.feedback import Feedback
from app.db.session import SessionLocal
from app.prompts import classifier_prompt
from app.repositories import feedback_repo, prediction_repo, upload_repo
from app.services import ai_service, contradiction_service, dashboard_service, duplicate_service, ingestion_service

logger = logging.getLogger(__name__)
settings = get_settings()


def run(upload_id: uuid.UUID) -> None:
    db = SessionLocal()
    try:
        _run(db, upload_id)
    except Exception as exc:
        logger.exception("Pipeline failed for upload %s", upload_id)
        db.rollback()
        from app.db.models.upload import Upload

        upload = db.get(Upload, upload_id)
        if upload is not None:
            _fail_upload(db, upload, upload.current_stage or "unknown", str(exc))
    finally:
        db.close()


def _fail_upload(db: Session, upload, stage: str, detail: str) -> None:
    upload_repo.set_stage(db, upload, stage=stage, status="failed", detail=detail)


def _run(db: Session, upload_id: uuid.UUID) -> None:
    from app.db.models.upload import Upload

    upload = db.get(Upload, upload_id)
    if upload is None:
        logger.error("Pipeline invoked for missing upload %s", upload_id)
        return

    upload_repo.mark_processing(db, upload)

    # --- Cleaning Data ---
    upload_repo.set_stage(db, upload, stage="cleaning_data", status="started")
    all_rows = feedback_repo.list_for_upload(db, upload_id)
    clean_rows: list[Feedback] = []
    dropped = 0
    for row in all_rows:
        cleaned = ingestion_service.clean_text(row.raw_text)
        if cleaned is None:
            dropped += 1
            continue
        db.query(Feedback).filter(Feedback.id == row.id).update({"cleaned_text": cleaned})
        row.cleaned_text = cleaned
        clean_rows.append(row)
    db.commit()
    upload_repo.increment_processed(db, upload, failed=dropped)
    upload_repo.set_stage(db, upload, stage="cleaning_data", status="completed", detail=f"dropped={dropped}")

    if not clean_rows:
        _fail_upload(db, upload, "cleaning_data", "No usable feedback text after cleaning.")
        return

    # --- Removing Duplicates (cheap exact-match pass) ---
    upload_repo.set_stage(db, upload, stage="removing_duplicates", status="started")
    seen_text: dict[str, uuid.UUID] = {}
    unique_rows: list[Feedback] = []
    for row in clean_rows:
        key = row.cleaned_text.lower().strip()
        if key in seen_text:
            db.query(Feedback).filter(Feedback.id == row.id).update(
                {"is_duplicate_of": seen_text[key]}
            )
        else:
            seen_text[key] = row.id
            unique_rows.append(row)
    db.commit()
    upload_repo.set_stage(
        db, upload, stage="removing_duplicates", status="completed",
        detail=f"exact_duplicates_removed={len(clean_rows) - len(unique_rows)}",
    )

    # --- Running AI ---
    upload_repo.set_stage(db, upload, stage="running_ai", status="started")
    themes_by_id: dict[uuid.UUID, str] = {}
    sentiments_by_id: dict[uuid.UUID, str] = {}
    processed = 0
    for batch_start in range(0, len(unique_rows), classifier_prompt.BATCH_SIZE):
        batch = unique_rows[batch_start : batch_start + classifier_prompt.BATCH_SIZE]
        call_items = [{"id": str(row.id), "text": row.cleaned_text} for row in batch]
        results = ai_service.classify_batch(call_items)
        for row, (result, processing_ms, raw_failed) in zip(batch, results):
            prediction_repo.save_prediction(
                db,
                feedback_id=row.id,
                result=result,
                processing_time_ms=processing_ms,
                prompt_version=classifier_prompt.PROMPT_VERSION,
                model_name=settings.openai_model,
                raw_llm_response=raw_failed,
            )
            themes_by_id[row.id] = result.theme
            sentiments_by_id[row.id] = result.sentiment
            processed += 1
        upload_repo.increment_processed(db, upload, processed=len(batch))
    upload_repo.set_stage(db, upload, stage="running_ai", status="completed", detail=f"classified={processed}")

    # --- Extracting Themes (theme-aware semantic dedup + contradiction detection) ---
    upload_repo.set_stage(db, upload, stage="extracting_themes", status="started")
    try:
        groups_created = duplicate_service.run_duplicate_detection(
            db, upload_id=upload_id, feedback_rows=unique_rows, themes_by_feedback_id=themes_by_id
        )
        contradictions_created = contradiction_service.run_contradiction_detection(
            db,
            upload_id=upload_id,
            feedback_rows=unique_rows,
            themes_by_feedback_id=themes_by_id,
            sentiments_by_feedback_id=sentiments_by_id,
        )
        detail = f"duplicate_groups={groups_created}, contradictions={contradictions_created}"
    except Exception as exc:  # dedup/contradiction failures should not abort the whole upload
        logger.exception("Duplicate/contradiction detection failed for upload %s", upload_id)
        detail = f"failed: {exc}"
    upload_repo.set_stage(db, upload, stage="extracting_themes", status="completed", detail=detail)

    # --- Generating Summary + Saving Database + Dashboard Ready ---
    upload_repo.set_stage(db, upload, stage="generating_summary", status="started")
    dashboard_service.refresh_snapshot(db, user_id=upload.user_id, upload_id=upload_id)
    upload_repo.set_stage(db, upload, stage="generating_summary", status="completed")

    upload_repo.set_stage(db, upload, stage="saving_database", status="started")
    upload_repo.set_stage(db, upload, stage="saving_database", status="completed")

    dashboard_service.refresh_snapshot(db, user_id=upload.user_id, upload_id=None)  # all-time snapshot too
    upload_repo.mark_completed(db, upload)
    upload_repo.set_stage(db, upload, stage="dashboard_ready", status="completed")
