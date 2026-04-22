# SQLAlchemy
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
# Python
from datetime import datetime
# Local
from app.models.base import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    vacancies = relationship("Vacancy", back_populates="user")
    posts = relationship("Post", back_populates="user")
    tasks = relationship("Task", back_populates="user")
    interview_sessions = relationship("InterviewSession", back_populates="user")
    posts = relationship(
    "Post",
    back_populates="user"
    )

    comments = relationship(
        "Comment",
        back_populates="user"
    )

    likes = relationship(
        "PostLike",
        back_populates="user"
    )