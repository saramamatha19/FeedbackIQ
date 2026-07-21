import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.db.models.user import User
from app.schemas.feedback import FeedbackOut, PredictionOut
from app.schemas.nl_query import NLQueryRequest, NLQueryResponse
from app.services import ai_service, nl_query_service

router = APIRouter(prefix="/query", tags=["query"])


@router.post("/nl", response_model=NLQueryResponse)
def query_nl(payload: NLQueryRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    today_iso = datetime.date.today().isoformat()
    nl_filter = ai_service.translate_nl_query(payload.query, today_iso=today_iso)
    rows = nl_query_service.run_nl_query(db, user_id=user.id, nl_filter=nl_filter)

    results = []
    for feedback, prediction in rows:
        item = FeedbackOut.model_validate(feedback)
        item.prediction = PredictionOut.model_validate(prediction)
        results.append(item)

    return NLQueryResponse(
        filters_applied=nl_filter.model_dump(),
        result_count=len(results),
        results=results,
    )
