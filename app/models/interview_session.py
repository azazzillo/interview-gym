# SQLAlchemy
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

# Python
from datetime import datetime

# Local
from app.models.base import Base


class InterviewSession(Base):
    __tablename__ = "interview_session"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id"),
        nullable=False
    )

    # NEW
    vacancy: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    level: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    language: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="ru"
    )

    question_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=7
    )

    status: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="interview_sessions"
    )

    messages = relationship(
        "InterviewMessage",
        back_populates="session"
    )

    report = relationship(
        "InterviewReport",
        back_populates="session",
        uselist=False
    )

    vacancies = relationship(
        "SessionVacancy",
        back_populates="session"
    )