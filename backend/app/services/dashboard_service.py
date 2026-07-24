"""
Aggregates feedback + predictions into the dashboard's precomputed snapshot
(dashboard_snapshots.snapshot_data), so dashboard reads are cheap JSONB reads
instead of live aggregation over potentially thousands of rows. Regenerated
at the end of the ingestion pipeline ("Dashboard Ready" stage) and on-demand
via ?refresh=true.
"""

import uuid
from collections import Counter, defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.contradiction import ContradictionPair
from app.db.models.dashboard import DashboardSnapshot
from app.db.models.duplicate import DuplicateGroup
from app.db.models.feedback import Feedback
from app.db.models.prediction import AIPrediction
from app.services import ai_service


def _current_predictions(db: Session, user_id: uuid.UUID | None, upload_id: uuid.UUID | None):
    stmt = (
        select(Feedback, AIPrediction)
        .join(AIPrediction, AIPrediction.feedback_id == Feedback.id)
        .where(AIPrediction.is_current.is_(True))
    )
    if user_id is not None:
        stmt = stmt.where(Feedback.user_id == user_id)
    if upload_id is not None:
        stmt = stmt.where(Feedback.upload_id == upload_id)
    return db.execute(stmt).all()


def build_snapshot(db: Session, *, user_id: uuid.UUID | None, upload_id: uuid.UUID | None = None) -> dict:
    """user_id=None aggregates across every user (admin cross-user view)."""
    rows = _current_predictions(db, user_id, upload_id)

    total = len(rows)
    category_counts = Counter()
    sentiment_counts = Counter()
    urgency_counts = Counter()
    emotion_counts = Counter()
    theme_counts = Counter()
    sentiment_by_theme: dict[str, Counter] = defaultdict(Counter)
    confidences = []
    severity_scores = []
    severity_map = {"Minor": 1, "Moderate": 4, "Major": 7, "Blocker": 10}
    feature_requests = Counter()
    bug_themes: dict[str, dict] = {}

    for feedback, pred in rows:
        category_counts[pred.category] += 1
        sentiment_counts[pred.sentiment] += 1
        urgency_counts[pred.urgency] += 1
        emotion_counts[pred.emotion] += 1
        theme_counts[pred.theme] += 1
        sentiment_by_theme[pred.theme][pred.sentiment] += 1
        confidences.append(pred.confidence_score)
        severity_scores.append(severity_map.get(pred.severity, 1))

        if pred.category == "Feature Request":
            feature_requests[pred.theme] += 1

        if pred.category == "Bug":
            bucket = bug_themes.setdefault(
                pred.theme,
                {"theme": pred.theme, "occurrences": 0, "max_severity": 0, "urgent_count": 0,
                 "latest_occurrence": None},
            )
            bucket["occurrences"] += 1
            bucket["max_severity"] = max(bucket["max_severity"], severity_map.get(pred.severity, 1))
            if pred.urgency in ("High", "Critical"):
                bucket["urgent_count"] += 1
            created = feedback.created_at.isoformat() if feedback.created_at else None
            if created and (bucket["latest_occurrence"] is None or created > bucket["latest_occurrence"]):
                bucket["latest_occurrence"] = created

    upload_ids = {feedback.upload_id for feedback, _pred in rows}
    duplicate_group_count = 0
    contradiction_count = 0
    if upload_ids:
        duplicate_group_count = (
            db.query(DuplicateGroup).filter(DuplicateGroup.upload_id.in_(upload_ids)).count()
        )
        contradiction_count = (
            db.query(ContradictionPair).filter(ContradictionPair.upload_id.in_(upload_ids)).count()
        )

    bug_leaderboard = sorted(
        bug_themes.values(),
        key=lambda b: (b["urgent_count"], b["max_severity"], b["occurrences"]),
        reverse=True,
    )[:10]
    feature_request_ranking = [
        {"theme": theme, "votes": count} for theme, count in feature_requests.most_common(10)
    ]
    top_themes = [{"theme": theme, "count": count} for theme, count in theme_counts.most_common(10)]

    aggregate_for_summary = {
        "theme_counts": dict(theme_counts),
        "sentiment_by_theme": {theme: dict(counts) for theme, counts in sentiment_by_theme.items()},
        "top_duplicate_clusters": [],
        "contradictions": [{"count": contradiction_count}] if contradiction_count else [],
    }
    if total > 0:
        key_signals = ai_service.generate_key_signals(aggregate_for_summary)
    else:
        key_signals = [
            {
                "headline": "No feedback yet",
                "detail": "Upload some feedback to see AI-generated signals here.",
                "supporting_theme": "Other",
                "severity_hint": "info",
            }
            for _ in range(3)
        ]

    snapshot = {
        "overview": {
            "total_feedback": total,
            "positive": sentiment_counts.get("Positive", 0),
            "neutral": sentiment_counts.get("Neutral", 0),
            "negative": sentiment_counts.get("Negative", 0),
            "urgent": urgency_counts.get("High", 0) + urgency_counts.get("Critical", 0),
            "avg_confidence": round(sum(confidences) / len(confidences), 1) if confidences else 0,
            "avg_severity": round(sum(severity_scores) / len(severity_scores), 1) if severity_scores else 0,
            "duplicate_groups": duplicate_group_count,
            "contradictions": contradiction_count,
        },
        "category_breakdown": [{"category": c, "count": n} for c, n in category_counts.most_common()],
        "sentiment_distribution": [{"sentiment": s, "count": n} for s, n in sentiment_counts.most_common()],
        "emotion_distribution": [{"emotion": e, "count": n} for e, n in emotion_counts.most_common()],
        "top_themes": top_themes,
        "feature_request_ranking": feature_request_ranking,
        "bug_leaderboard": bug_leaderboard,
        "key_signals": key_signals,
    }
    return snapshot


def build_admin_snapshot(db: Session) -> dict:
    """Live cross-user aggregate for the admin dashboard. Not cached in dashboard_snapshots,
    which is keyed to a single user_id — admin traffic is low-volume enough to compute on read."""
    return build_snapshot(db, user_id=None, upload_id=None)


def refresh_snapshot(db: Session, *, user_id: uuid.UUID, upload_id: uuid.UUID | None = None) -> DashboardSnapshot:
    snapshot_data = build_snapshot(db, user_id=user_id, upload_id=upload_id)
    snapshot = DashboardSnapshot(user_id=user_id, upload_id=upload_id, snapshot_data=snapshot_data)
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    return snapshot


def get_latest_snapshot(db: Session, *, user_id: uuid.UUID, upload_id: uuid.UUID | None) -> DashboardSnapshot | None:
    stmt = (
        select(DashboardSnapshot)
        .where(DashboardSnapshot.user_id == user_id, DashboardSnapshot.upload_id == upload_id)
        .order_by(DashboardSnapshot.created_at.desc())
        .limit(1)
    )
    return db.scalar(stmt)
'''
"The dashboard_service.py file is responsible for generating the dashboard data.
 It reads the latest AI predictions from the database, aggregates them into metrics like category counts, 
 sentiment distribution, top themes, duplicate and contradiction counts, and bug rankings. 
 It then sends only these aggregated statistics to the LLM to generate three key insights, combines everything 
 into a single JSON snapshot, 
 stores it in the DashboardSnapshot table,
 and the frontend simply reads this cached snapshot instead of recomputing all analytics on every request."'''