from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class QuestionResponse(BaseModel):
    id: int
    session_id: int
    difficulty: str
    question_text: str
    asked_at: datetime

    class Config:
        from_attributes = True


class AnswerSubmit(BaseModel):
    question_id: int
    user_answer: str
    time_taken_seconds: int = 0


class AnswerResponse(BaseModel):
    question_id: int
    is_correct: bool
    explanation: str
    correct_answer: str
    session_complete: bool = False
    difficulty_changed: bool = False
    new_difficulty: Optional[str] = None


class CreateSessionResponse(BaseModel):
    session_id: int
    started_at: datetime


class SessionSummary(BaseModel):
    session_id: int
    started_at: datetime
    ended_at: Optional[datetime]
    current_difficulty: str
    total_questions: int
    correct_answers: int
    wrong_answers: int
    accuracy: float = 0.0


class SessionReview(BaseModel):
    session_id: int
    total_questions: int
    correct_answers: int
    wrong_answers: int
    accuracy: float
    difficulty_progression: List[str]
    questions: List["QuestionReviewItem"]
    recommendations: List[str]
    weak_areas: List[str]
    strong_areas: List[str]


class QuestionReviewItem(BaseModel):
    question_id: int
    difficulty: str
    question_text: str
    user_answer: str
    correct_answer: str
    is_correct: bool
    explanation: str


class DashboardData(BaseModel):
    daily: "PeriodStats"
    weekly: "PeriodStats"
    monthly: "PeriodStats"
    trend_data: List["TrendPoint"]


class PeriodStats(BaseModel):
    total_questions: int = 0
    correct_answers: int = 0
    wrong_answers: int = 0
    accuracy: float = 0.0
    sessions: int = 0


class TrendPoint(BaseModel):
    date: str
    accuracy: float
    questions_answered: int
    average_difficulty: float
