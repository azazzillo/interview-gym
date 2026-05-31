from sqlalchemy.orm import Session

from app.models import (
    InterviewSession,
    InterviewMessage,
    InterviewReport
)


# =========================
# SESSION
# =========================

def create_session(
    db: Session,
    user_id: int,
    vacancy: str,
    level: str,
    language: str,
    question_count: int,
):
    session = InterviewSession(
        user_id=user_id,
        vacancy=vacancy,
        level=level,
        language=language,
        question_count=question_count,
        status="active"
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session

def get_session(db: Session, session_id: int):
    return (
        db.query(InterviewSession)
        .filter(InterviewSession.id == session_id)
        .first()
    )


# =========================
# MESSAGE
# =========================

def create_message(
    db: Session,
    session_id: int,
    sender: str,
    content: str,
    audio_url: str | None = None
):
    message = InterviewMessage(
        session_id=session_id,
        sender=sender,
        content=content,
        audio_url=audio_url
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


def get_messages(db: Session, session_id: int):
    return (
        db.query(InterviewMessage)
        .filter(InterviewMessage.session_id == session_id)
        .all()
    )


# =========================
# REPORT
# =========================

def create_report(
    db: Session,
    session_id: int,
    overall_score: int,
    confidence_score: int,
    technical_score: int,
    communication_score: int,
    feedback: str
):
    report = InterviewReport(
        session_id=session_id,
        overall_score=overall_score,
        confidence_score=confidence_score,
        technical_score=technical_score,
        communication_score=communication_score,
        feedback=feedback
    )

    db.add(report)

    session = get_session(db, session_id)
    session.status = "finished"

    db.commit()
    db.refresh(report)

    return report