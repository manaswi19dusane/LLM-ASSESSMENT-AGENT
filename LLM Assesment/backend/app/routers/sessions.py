from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from app.core.database import get_db
from app.models.schemas import Session, Question, Difficulty
from app.models.pydantic_models import (
    CreateSessionResponse,
    SessionSummary,
    SessionReview,
    QuestionReviewItem,
)
from app.services.openrouter import openrouter_service

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.post("", response_model=CreateSessionResponse)
def create_session(db: DBSession = Depends(get_db)):
    session = Session(current_difficulty=Difficulty.beginner)
    db.add(session)
    db.commit()
    db.refresh(session)
    return CreateSessionResponse(
        session_id=session.id,
        started_at=session.started_at,
    )


@router.get("", response_model=list[SessionSummary])
def list_sessions(db: DBSession = Depends(get_db)):
    sessions = db.query(Session).order_by(Session.started_at.desc()).limit(50).all()
    result = []
    for s in sessions:
        total = s.total_questions or 1
        result.append(SessionSummary(
            session_id=s.id,
            started_at=s.started_at,
            ended_at=s.ended_at,
            current_difficulty=s.current_difficulty.value,
            total_questions=s.total_questions,
            correct_answers=s.correct_answers,
            wrong_answers=s.wrong_answers,
            accuracy=round((s.correct_answers / total) * 100, 1),
        ))
    return result


@router.get("/{session_id}", response_model=SessionSummary)
def get_session(session_id: int, db: DBSession = Depends(get_db)):
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    total = session.total_questions or 1
    return SessionSummary(
        session_id=session.id,
        started_at=session.started_at,
        ended_at=session.ended_at,
        current_difficulty=session.current_difficulty.value,
        total_questions=session.total_questions,
        correct_answers=session.correct_answers,
        wrong_answers=session.wrong_answers,
        accuracy=round((session.correct_answers / total) * 100, 1),
    )


@router.delete("/{session_id}")
def delete_session(session_id: int, db: DBSession = Depends(get_db)):
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(session)
    db.commit()
    return {"ok": True}


@router.get("/{session_id}/review", response_model=SessionReview)
async def get_session_review(session_id: int, db: DBSession = Depends(get_db)):
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    questions = db.query(Question).filter(
        Question.session_id == session_id,
        Question.user_answer.isnot(None),
    ).order_by(Question.asked_at).all()

    items = [
        QuestionReviewItem(
            question_id=q.id,
            difficulty=q.difficulty.value,
            question_text=q.question_text,
            user_answer=q.user_answer or "",
            correct_answer=q.correct_answer,
            is_correct=bool(q.is_correct),
            explanation=q.explanation or "",
        )
        for q in questions
    ]

    total = len(questions) or 1
    correct = sum(1 for q in questions if q.is_correct)
    wrong = total - correct

    progression = []
    current_val = None
    for q in questions:
        v = q.difficulty.value
        if v != current_val:
            progression.append(v)
            current_val = v

    session_data = {
        "session_id": session_id,
        "total_questions": total,
        "correct_answers": correct,
        "wrong_answers": wrong,
        "accuracy": round((correct / total) * 100, 1),
        "difficulty_progression": progression,
        "questions": [
            {
                "difficulty": q.difficulty.value,
                "question": q.question_text[:100],
                "is_correct": bool(q.is_correct),
            }
            for q in questions
        ],
    }

    review_data = await openrouter_service.generate_review(session_data)

    return SessionReview(
        session_id=session_id,
        total_questions=total,
        correct_answers=correct,
        wrong_answers=wrong,
        accuracy=round((correct / total) * 100, 1),
        difficulty_progression=progression,
        questions=items,
        recommendations=review_data.get("recommendations", []),
        weak_areas=review_data.get("weak_areas", []),
        strong_areas=review_data.get("strong_areas", []),
    )
