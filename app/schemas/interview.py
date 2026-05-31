from pydantic import BaseModel
from datetime import datetime


# =========================
# START INTERVIEW
# =========================

class InterviewStartResponse(BaseModel):
    session_id: int
    question: str
    audio_url: str | None = None


# =========================
# ANSWER INTERVIEW
# =========================

class InterviewAnswerResponse(BaseModel):
    question: str | None = None
    audio_url: str | None = None

    is_finished: bool = False

    report: dict | None = None


# =========================
# MESSAGE
# =========================

class InterviewMessageResponse(BaseModel):
    id: int
    sender: str
    content: str
    audio_url: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


# =========================
# REPORT
# =========================

class InterviewReportResponse(BaseModel):
    overall_score: int | None = None
    confidence_score: int | None = None
    technical_score: int | None = None
    communication_score: int | None = None

    feedback: str | None = None

    class Config:
        from_attributes = True


class FinishRequest(BaseModel):
    session_id: int


class StartInterviewRequest(BaseModel):
    vacancy: str
    level: str
    language: str
    question_count: int


class InterviewStartResponse(BaseModel):
    session_id: int
    question: str
    audio_url: str | None = None
