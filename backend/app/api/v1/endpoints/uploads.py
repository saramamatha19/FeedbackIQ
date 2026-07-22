import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.models.user import User
from app.db.session import get_db
from app.repositories import feedback_repo, upload_repo
from app.schemas.upload import UploadOut, UploadStatusOut
from app.services import ingestion_service, pipeline_service

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post("/csv", response_model=UploadOut, status_code=202)
async def upload_csv(
    background_tasks: BackgroundTasks,
    file: UploadFile,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    filename = file.filename.lower()
    if filename.endswith(".csv"):
        source_type = "csv"
        parse = ingestion_service.parse_csv
    elif filename.endswith(".xlsx"):
        source_type = "xlsx"
        parse = ingestion_service.parse_xlsx
    else:
        raise HTTPException(status_code=400, detail="Please upload a .csv or .xlsx file.")

    file_bytes = await file.read()
    try:
        texts = parse(file_bytes)
    except ingestion_service.InvalidFileError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    upload = upload_repo.create(
        db, user_id=user.id, source_type=source_type, original_filename=file.filename, total_rows=len(texts)
    )
    upload_repo.set_stage(db, upload, stage="reading_file", status="completed", detail=f"rows={len(texts)}")
    feedback_repo.create_many(db, upload_id=upload.id, user_id=user.id, texts=texts)

    background_tasks.add_task(pipeline_service.run, upload.id)
    return upload


@router.get("/{upload_id}/status", response_model=UploadStatusOut)
def get_upload_status(upload_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    upload = upload_repo.get(db, upload_id, user.id)
    if upload is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Upload not found")
    return upload


@router.get("/{upload_id}", response_model=UploadOut)
def get_upload(upload_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    upload = upload_repo.get(db, upload_id, user.id)
    if upload is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Upload not found")
    return upload


@router.get("", response_model=list[UploadOut])
def list_uploads(
    limit: int = 50, offset: int = 0, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return upload_repo.list_for_user(db, user.id, limit=limit, offset=offset)
