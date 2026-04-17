# SQLAlchemy
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
# Python
from datetime import datetime
# Local
from app.models.base import Base


class TaskSubmission(Base):
    __tablename__ = "task_submission"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("task.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)

    solution_text: Mapped[str | None] = mapped_column(String, nullable=True)
    repo_url: Mapped[str | None] = mapped_column(String, nullable=True)
    archive_url: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="submissions")
    result = relationship("TaskResult", back_populates="submission", uselist=False)