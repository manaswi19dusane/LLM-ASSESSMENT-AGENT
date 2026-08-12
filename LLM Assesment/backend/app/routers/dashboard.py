from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import func

from app.core.database import get_db
from app.models.schemas import Session, Question, Difficulty
from app.models.pydantic_models import (
    DashboardData,
    PeriodStats,
    TrendPoint,
)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def _get_period_stats(
    db: DBSession,
    since: datetime,
) -> PeriodStats:
    questions = (
        db.query(Question)
        .join(Session, Question.session_id == Session.id)
        .filter(
            Question.answered_at >= since,
            Question.user_answer.isnot(None),
        )
        .all()
    )

    total = len(questions)
    correct = sum(1 for q in questions if q.is_correct)
    wrong = total - correct

    session_count = (
        db.query(Session)
        .filter(Session.started_at >= since)
        .count()
    )

    return PeriodStats(
        total_questions=total,
        correct_answers=correct,
        wrong_answers=wrong,
        accuracy=round((correct / total) * 100, 1) if total > 0 else 0.0,
        sessions=session_count,
    )


DIFF_MAP = {"beginner": 0, "intermediate": 1, "advanced": 2, "expert": 3}


@router.get("", response_model=DashboardData)
def get_dashboard(db: DBSession = Depends(get_db)):
    now = datetime.now(timezone.utc)

    daily = _get_period_stats(db, now - timedelta(days=1))
    weekly = _get_period_stats(db, now - timedelta(days=7))
    monthly = _get_period_stats(db, now - timedelta(days=30))

    last_30_days = now - timedelta(days=30)
    rows = (
        db.query(
            func.date(Question.answered_at).label("day"),
            func.count(Question.id).label("count"),
            func.sum(Question.is_correct).label("correct"),
        )
        .filter(
            Question.answered_at >= last_30_days,
            Question.user_answer.isnot(None),
        )
        .group_by(func.date(Question.answered_at))
        .order_by(func.date(Question.answered_at))
        .all()
    )

    from collections import defaultdict
    day_questions = defaultdict(list)
    all_trend = (
        db.query(Question)
        .filter(
            Question.answered_at >= last_30_days,
            Question.user_answer.isnot(None),
        )
        .order_by(Question.answered_at)
        .all()
    )
    for q in all_trend:
        key = q.answered_at.strftime("%Y-%m-%d")
        day_questions[key].append(q)

    trend_data = []
    for row in rows:
        day_str = str(row.day)
        qs = day_questions.get(day_str, [])
        avg_diff = 0.0
        if qs:
            vals = []
            for q in qs:
                d = q.difficulty
                if hasattr(d, 'value'):
                    vals.append(DIFF_MAP.get(d.value, 0))
                else:
                    vals.append(DIFF_MAP.get(str(d), 0))
            avg_diff = sum(vals) / len(vals)
        trend_data.append(TrendPoint(
            date=day_str,
            accuracy=round((row.correct / row.count) * 100, 1) if row.count > 0 else 0.0,
            questions_answered=row.count,
            average_difficulty=round(avg_diff, 2),
        ))

    return DashboardData(
        daily=daily,
        weekly=weekly,
        monthly=monthly,
        trend_data=trend_data,
    )
