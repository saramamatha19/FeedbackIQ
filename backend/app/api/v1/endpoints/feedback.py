import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import get_current_user
from app.db.models.user import User
from app.db.session import get_db
from app.prompts import classifier_prompt
from app.repositories import feedback_repo, prediction_repo, upload_repo
from app.schemas.feedback import FeedbackOut, PredictionOut, SingleFeedbackRequest, SingleFeedbackResponse
from app.schemas.upload import PasteFeedbackRequest, UploadOut
from app.services import ai_service, dashboard_service, ingestion_service, pipeline_service

router = APIRouter(tags=["feedback"])
settings = get_settings()


@router.post("/feedback/single", response_model=SingleFeedbackResponse, status_code=201)
def submit_single_feedback(
    payload: SingleFeedbackRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    cleaned = ingestion_service.clean_text(payload.text)
    if cleaned is None:
        raise HTTPException(status_code=422, detail="Feedback text is empty after cleaning.")

    upload = upload_repo.create(db, user_id=user.id, source_type="single", total_rows=1)
    upload_repo.set_stage(db, upload, stage="reading_file", status="completed")
    upload_repo.mark_processing(db, upload)

    feedback_rows = feedback_repo.create_many(db, upload_id=upload.id, user_id=user.id, texts=[payload.text])
    feedback = feedback_rows[0]
    feedback.cleaned_text = cleaned
    db.commit()

    results = ai_service.classify_batch([{"id": str(feedback.id), "text": cleaned}])
    result, processing_ms, raw_failed = results[0]
    prediction = prediction_repo.save_prediction(
        db,
        feedback_id=feedback.id,
        result=result,
        processing_time_ms=processing_ms,
        prompt_version=classifier_prompt.PROMPT_VERSION,
        model_name=settings.openai_model,
        raw_llm_response=raw_failed,
    )

    upload_repo.increment_processed(db, upload, processed=1)
    upload_repo.mark_completed(db, upload)
    dashboard_service.refresh_snapshot(db, user_id=user.id, upload_id=None)

    return SingleFeedbackResponse(
        feedback=FeedbackOut.model_validate(feedback), prediction=PredictionOut.model_validate(prediction)
    )


@router.post("/feedback/paste", response_model=UploadOut, status_code=202)
def submit_paste_feedback(
    payload: PasteFeedbackRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    items = ai_service.split_feedback_blob(payload.raw_text)
    if not items:
        raise HTTPException(status_code=422, detail="Could not extract any feedback from the pasted text.")

    upload = upload_repo.create(db, user_id=user.id, source_type="paste", total_rows=len(items))
    upload_repo.set_stage(db, upload, stage="reading_file", status="completed", detail=f"rows={len(items)}")
    feedback_repo.create_many(db, upload_id=upload.id, user_id=user.id, texts=items)

    background_tasks.add_task(pipeline_service.run, upload.id)
    return upload


@router.get("/feedback", response_model=list[FeedbackOut])
def list_feedback(
    upload_id: uuid.UUID | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    rows = feedback_repo.list_with_current_predictions(
        db, user_id=user.id, upload_id=upload_id, limit=limit, offset=offset
    )
    labels = upload_repo.source_label_map(db, user.id)
    out = []
    for row in rows:
        current = next((p for p in row.predictions if p.is_current), None)
        item = FeedbackOut.model_validate(row)
        item.prediction = PredictionOut.model_validate(current) if current else None
        item.source_label = labels.get(row.upload_id, "")
        out.append(item)
    return out


@router.get("/feedback/{feedback_id}", response_model=FeedbackOut)
def get_feedback(feedback_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = feedback_repo.get(db, feedback_id, user.id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")
    current = feedback_repo.current_prediction_for(db, feedback_id)
    item = FeedbackOut.model_validate(row)
    item.prediction = PredictionOut.model_validate(current) if current else None
    return item


@router.post("/feedback/{feedback_id}/rerun", response_model=PredictionOut)
def rerun_feedback(feedback_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = feedback_repo.get(db, feedback_id, user.id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")

    text = row.cleaned_text or row.raw_text
    results = ai_service.classify_batch([{"id": str(row.id), "text": text}])
    result, processing_ms, raw_failed = results[0]
    prediction = prediction_repo.save_prediction(
        db,
        feedback_id=row.id,
        result=result,
        processing_time_ms=processing_ms,
        prompt_version=classifier_prompt.PROMPT_VERSION,
        model_name=settings.openai_model,
        raw_llm_response=raw_failed,
    )
    return prediction


@router.get("/feedback/{feedback_id}/predictions/history", response_model=list[PredictionOut])
def prediction_history(feedback_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = feedback_repo.get(db, feedback_id, user.id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")
    return prediction_repo.history_for_feedback(db, feedback_id)
