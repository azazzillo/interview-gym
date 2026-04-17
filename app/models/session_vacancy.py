# SQLAlchemy
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
# Python
from datetime import datetime
# Local
from app.models.base import Base


class SessionVacancy(Base):
    __tablename__ = "session_vacancy"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("interview_session.id"), nullable=False)
    vacancy_id: Mapped[int] = mapped_column(Integer, ForeignKey("vacancy.id"), nullable=False)

    session = relationship("InterviewSession", back_populates="vacancies")
    vacancy = relationship("Vacancy", back_populates="session_links")