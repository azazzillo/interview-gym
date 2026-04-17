# SQLAlchemy
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
# Python
from datetime import datetime
# Local
from app.models.base import Base


class TaskResult(Base):
    __tablename__ = "task_result"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    submission_id: Mapped[int] = mapped_column(Integer, ForeignKey("task_submission.id"), nullable=False)

    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    architecture_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    code_quality_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    correctness_score: Mapped[int | None] = mapped_column(Integer, nullable=True)

    feedback: Mapped[str | None] = mapped_column(String, nullable=True)
    improvements: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    submission = relationship("TaskSubmission", back_populates="result")