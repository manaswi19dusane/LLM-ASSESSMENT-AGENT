from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class Difficulty(str, enum.Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"
    expert = "expert"


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    ended_at = Column(DateTime, nullable=True)
    current_difficulty = Column(SAEnum(Difficulty), default=Difficulty.beginner)
    total_questions = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    wrong_answers = Column(Integer, default=0)
    consecutive_correct = Column(Integer, default=0)

    questions = relationship("Question", back_populates="session", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    difficulty = Column(SAEnum(Difficulty))
    question_text = Column(Text)
    correct_answer = Column(Text)
    user_answer = Column(Text, nullable=True)
    is_correct = Column(Integer, nullable=True)
    explanation = Column(Text, nullable=True)
    asked_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    answered_at = Column(DateTime, nullable=True)
    time_taken_seconds = Column(Integer, nullable=True)

    session = relationship("Session", back_populates="questions")
