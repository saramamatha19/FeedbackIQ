import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models.status_history import ProcessingStatusHistory
from app.db.models.upload import Upload


def create(db: Session, *, user_id: uuid.UUID, source_type: str, original_filename: str | None = None,
           display_name: str | None = None, total_rows: int = 0) -> Upload:
    upload = Upload(
        user_id=user_id,
        source_type=source_type,
        original_filename=original_filename,
        display_name=display_name,
        total_rows=total_rows,
        status="pending",
    )
    db.add(upload)
    db.commit()
    db.refresh(upload)
    return upload


def get(db: Session, upload_id: uuid.UUID, user_id: uuid.UUID) -> Upload | None:
    return db.scalar(
        select(Upload).where(Upload.id == upload_id, Upload.user_id == user_id)
    )


def list_for_user(db: Session, user_id: uuid.UUID, *, limit: int = 50, offset: int = 0) -> list[Upload]:
    return list(
        db.scalars(
            select(Upload)
            .where(Upload.user_id == user_id)
            .order_by(Upload.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
    )


def source_label_map(db: Session, user_id: uuid.UUID) -> dict[uuid.UUID, str]:
    """Maps each of the user's upload ids to an ordinal label like 'single_1', 'paste_2', 'csv_1'."""
    row_number = func.row_number().over(partition_by=Upload.source_type, order_by=Upload.created_at).label("rn")
    stmt = select(Upload.id, Upload.source_type, row_number).where(Upload.user_id == user_id)
    return {row.id: f"{row.source_type}_{row.rn}" for row in db.execute(stmt)}


def set_stage(db: Session, upload: Upload, *, stage: str, status: str, detail: str | None = None) -> None:
    upload.current_stage = stage
    if status == "failed":
        upload.status = "failed"
        upload.error_message = detail
    db.add(ProcessingStatusHistory(upload_id=upload.id, stage=stage, status=status, detail=detail))
    db.commit()


def mark_processing(db: Session, upload: Upload) -> None:
    upload.status = "processing"
    db.commit()


def mark_completed(db: Session, upload: Upload) -> None:
    import datetime

    upload.status = "completed"
    upload.current_stage = "dashboard_ready"
    upload.completed_at = datetime.datetime.now(datetime.timezone.utc)
    db.commit()


def increment_processed(db: Session, upload: Upload, *, processed: int = 0, failed: int = 0) -> None:
    upload.processed_rows += processed
    upload.failed_rows += failed
    db.commit()
