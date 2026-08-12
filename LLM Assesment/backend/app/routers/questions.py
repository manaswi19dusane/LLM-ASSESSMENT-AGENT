from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from app.core.database import get_db
from app.models.schemas import Session, Question
from app.models.pydantic_models import QuestionResponse, AnswerSubmit, AnswerResponse
from app.services.question_service import (
    generate_question_for_session,
    verify_and_score,
    update_difficulty,
    end_session,
)

router = APIRouter(prefix="/api/questions", tags=["questions"])


@router.post("/next/{session_id}", response_model=QuestionResponse)
async def get_next_question(session_id: int, db: DBSession = Depends(get_db)):
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.ended_at:
        raise HTTPException(status_code=400, detail="Session has ended")

    question = await generate_question_for_session(db, session)
    if not question:
        raise HTTPException(status_code=500, detail="Failed to generate question")

    return QuestionResponse(
        id=question.id,
        session_id=question.session_id,
        difficulty=question.difficulty.value,
        question_text=question.question_text,
        asked_at=question.asked_at,
    )


@router.post("/answer", response_model=AnswerResponse)
async def submit_answer(
    answer_data: AnswerSubmit,
    db: DBSession = Depends(get_db),
):
    question = db.query(Question).filter(Question.id == answer_data.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    if question.user_answer is not None:
        raise HTTPException(status_code=400, detail="Question already answered")

    session = db.query(Session).filter(Session.id == question.session_id).first()

    is_correct, explanation = await verify_and_score(
        db, question, answer_data.user_answer, answer_data.time_taken_seconds
    )

    question.user_answer = answer_data.user_answer
    question.is_correct = 1 if is_correct else 0
    question.answered_at = datetime.now(timezone.utc)
    question.time_taken_seconds = answer_data.time_taken_seconds
    question.explanation = explanation

    if is_correct:
        session.correct_answers += 1
        session.consecutive_correct += 1
    else:
        session.wrong_answers += 1
        session.consecutive_correct = 0

    difficulty_changed = update_difficulty(session)
    new_difficulty = session.current_difficulty.value if difficulty_changed else None

    questions_in_session = db.query(Question).filter(
        Question.session_id == session.id,
    ).count()

    session_complete = questions_in_session >= 5 and (
        session.consecutive_correct == 0 or questions_in_session >= 20
    )

    if session_complete:
        end_session(db, session)

    db.commit()

    return AnswerResponse(
        question_id=question.id,
        is_correct=is_correct,
        explanation=question.explanation or explanation,
        correct_answer=question.correct_answer,
        session_complete=session_complete,
        difficulty_changed=difficulty_changed,
        new_difficulty=new_difficulty,
    )
