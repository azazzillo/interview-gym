# Python
import shutil
import uuid
import os
# FastAPI
from fastapi import APIRouter, Depends, UploadFile, File, Form, Body
from sqlalchemy.orm import Session
# Local
from app.services.gemini_service import generate_next_question
from app.services.whisper_service import transcribe_audio
from app.schemas.interview import FinishRequest, InterviewStartResponse, StartInterviewRequest
from app.services.interview_flow import get_initial_question
from app.services.gemini_service import generate_report
from app.services.tts_service import generate_tts
from app.orm import interview as interview_orm
from app.services.deps import get_current_user
from app.utils.json_parser import extract_json
from app.db import get_db



router = APIRouter(
    prefix="/api/interview",
    tags=["Interview"]
)


@router.post(
    "/start",
    response_model=InterviewStartResponse
)
async def start_interview(
    data: StartInterviewRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    session = interview_orm.create_session(
        db=db,
        user_id=current_user.id,
        vacancy=data.vacancy,
        level=data.level,
        language=data.language,
        question_count=data.question_count
    )

    initial_question = get_initial_question(
        vacancy=data.vacancy,
        level=data.level
    )

    interview_orm.create_message(
        db=db,
        session_id=session.id,
        sender="assistant",
        content=initial_question
    )

    audio_url = await generate_tts(
        initial_question
    )

    return {
        "session_id": session.id,
        "question": initial_question,
        "audio_url": audio_url,
        "total_questions": session.question_count
    }

UPLOAD_DIR = "media/user_audio"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)


@router.post("/answer")
async def answer_interview(
    session_id: int = Form(...),
    audio: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # =========================
    # SAVE AUDIO
    # =========================

    filename = f"{uuid.uuid4()}.webm"

    file_path = os.path.join(
        UPLOAD_DIR,
        filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(
            audio.file,
            buffer
        )

    # =========================
    # SPEECH TO TEXT
    # =========================

    user_text = await transcribe_audio(file_path)

    # =========================
    # SAVE USER MESSAGE
    # =========================

    interview_orm.create_message(
        db=db,
        session_id=session_id,
        sender="user",
        content=user_text
    )

    # =========================
    # GET DATA
    # =========================

    session = interview_orm.get_session(db, session_id)

    messages = interview_orm.get_messages(db, session_id)

    conversation = ""
    for msg in messages:
        conversation += f"{msg.sender}: {msg.content}\n"

    # =========================
    # CHECK LIMIT (🔥 FIX HERE)
    # =========================

    assistant_messages = [
        msg for msg in messages
        if msg.sender == "assistant"
    ]

    if len(assistant_messages) >= session.question_count:
        return {
            "is_finished": True
        }

    # =========================
    # GENERATE QUESTION
    # =========================

    next_question = generate_next_question(
        conversation=conversation,
        vacancy=session.vacancy,
        level=session.level,
        language=session.language
    )

    # =========================
    # SAVE AI MESSAGE
    # =========================

    interview_orm.create_message(
        db=db,
        session_id=session_id,
        sender="assistant",
        content=next_question
    )

    # =========================
    # GENERATE VOICE
    # =========================

    audio_url = await generate_tts(next_question)

    return {
        "question": next_question,
        "audio_url": audio_url,
        "is_finished": False
    }


@router.post("/finish")
async def finish_interview(
    data: FinishRequest = Body(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    session_id = data.session_id
    messages = interview_orm.get_messages(db, session_id)

    conversation = ""
    for msg in messages:
        conversation += f"{msg.sender}: {msg.content}\n"

    # =========================
    # GENERATE REPORT
    # =========================
    session = interview_orm.get_session(
        db,
        session_id
    )

    raw_report = generate_report(
        conversation=conversation,
        vacancy=session.vacancy,
        level=session.level
    )
    report_json = extract_json(raw_report)

    # =========================
    # SAVE REPORT (если есть таблица)
    # =========================
    interview_orm.create_report(
        db=db,
        session_id=session_id,
        overall_score=report_json["overall_score"],
        confidence_score=report_json["confidence_score"],
        technical_score=report_json["technical_score"],
        communication_score=report_json["communication_score"],
        feedback=report_json["feedback"]
    )

    return report_json


@router.get("/history")
async def get_history(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    sessions = (
        db.query(interview_orm.InterviewSession)
        .filter(interview_orm.InterviewSession.user_id == current_user.id)
        .order_by(interview_orm.InterviewSession.created_at.desc())
        .all()
    )

    result = []

    for s in sessions:
        report = s.report  # one-to-one

        messages = (
            db.query(interview_orm.InterviewMessage)
            .filter(interview_orm.InterviewMessage.session_id == s.id)
            .all()
        )

        assistant_count = len([
            m for m in messages if m.sender == "assistant"
        ])

        result.append({
            "id": s.id,
            "created_at": s.created_at,
            "status": s.status,

            # ⚠️ если этих полей нет — просто None
            "vacancy": getattr(s, "vacancy", None),
            "level": getattr(s, "level", None),

            "questions_count": assistant_count,

            "overall_score": report.overall_score if report else None,
        })

    return {"sessions": result}


@router.get("/{session_id}")
def get_session(session_id: int, db: Session = Depends(get_db)):
    session = interview_orm.get_session(db, session_id)

    return {
        "id": session.id,
        "vacancy": session.vacancy,
        "level": session.level,
        "created_at": session.created_at,
        "report": session.report
    }
