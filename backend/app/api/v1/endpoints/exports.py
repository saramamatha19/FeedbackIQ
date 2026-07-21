import csv
import io
import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.models.user import User
from app.db.session import get_db
from app.repositories import feedback_repo

router = APIRouter(prefix="/exports", tags=["exports"])

COLUMNS = [
    "id", "raw_text", "category", "sentiment", "emotion", "theme", "urgency",
    "severity", "business_impact", "customer_intent", "confidence_score",
    "suggested_action", "ai_explanation", "needs_human_review", "created_at",
]


@router.get("/feedback.csv")
def export_feedback_csv(
    upload_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    rows = feedback_repo.list_with_current_predictions(
        db, user_id=user.id, upload_id=upload_id, limit=5000, offset=0
    )

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(COLUMNS)
    for row in rows:
        prediction = next((p for p in row.predictions if p.is_current), None)
        writer.writerow(
            [
                row.id,
                row.raw_text,
                *(
                    [
                        prediction.category, prediction.sentiment, prediction.emotion,
                        prediction.theme, prediction.urgency, prediction.severity,
                        prediction.business_impact, prediction.customer_intent,
                        prediction.confidence_score, prediction.suggested_action,
                        prediction.ai_explanation, prediction.needs_human_review,
                    ]
                    if prediction
                    else [""] * 12
                ),
                row.created_at.isoformat(),
            ]
        )
    buffer.seek(0)

    filename = f"feedbackiq_export{'_' + str(upload_id) if upload_id else ''}.csv"
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
