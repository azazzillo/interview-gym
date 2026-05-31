import re
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.deps import get_current_user
from app.services.ai import generate_task, review_solution
from app.orm import task as task_orm
from app.schemas.task import (
    GenerateTaskRequest,
    SubmitTaskRequest,
    SubmitTaskResponse,
    TaskResponse,
)

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


def _task_to_response(task, submission=None) -> TaskResponse:
    """Конвертирует ORM-объект Task в TaskResponse для фронта."""

    # Достаём requirements из описания или из tech_stack если сохранили туда
    requirements = []
    score = None
    feedback = None
    status = "pending"
    solution = None

    # Если есть сабмишн — смотрим результат
    if submission:
        solution = submission.solution_text
        status = "submitted"
        if submission.result:
            score = submission.result.score
            feedback = submission.result.feedback
            status = "passed" if score and score >= 60 else "failed"

    # requirements хранятся в tech_stack как JSON-строка (см. create ниже)
    raw_requirements = []
    if task.tech_stack and task.tech_stack.startswith("["):
        try:
            raw_requirements = json.loads(task.tech_stack)
        except Exception:
            pass

    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        tech_stack=None,
        difficulty=task.difficulty,
        time_limit=task.time_limit,
        created_at=task.created_at,
        vacancy=task.difficulty,   # vacancy не хранится отдельно, используем difficulty как подпись
        level=task.difficulty,
        status=status,
        score=score,
        feedback=feedback,
        requirements=raw_requirements,
        solution=solution,
    )


@router.post("/generate")
async def generate(
    body: GenerateTaskRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        ai_data = await generate_task(
            vacancy=body.vacancy,
            level=body.level,
            topic=body.topic,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка AI: {str(e)}")

    # requirements сохраняем в tech_stack как JSON
    requirements_json = json.dumps(ai_data.get("requirements", []), ensure_ascii=False)

    task = task_orm.create_task(
        db=db,
        user_id=current_user.id,
        title=ai_data.get("title"),
        description=ai_data.get("description"),
        tech_stack=requirements_json,
        difficulty=f"{body.vacancy} · {body.level}",
        time_limit=ai_data.get("time_limit"),
    )

    response = _task_to_response(task)
    # Переопределяем vacancy/level для красивого отображения
    response.vacancy = body.vacancy
    response.level = body.level
    response.requirements = ai_data.get("requirements", [])

    return {"task": response}


@router.get("/")
def get_tasks(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    tasks = task_orm.get_tasks(db, user_id=current_user.id, page=page, limit=limit)

    result = []
    for task in tasks:
        # Берём последний сабмишн если есть
        last_submission = task.submissions[-1] if task.submissions else None
        result.append(_task_to_response(task, last_submission))

    return {"tasks": result}


@router.get("/{task_id}")
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    task = task_orm.get_task(db, task_id=task_id, user_id=current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Задание не найдено")

    last_submission = task.submissions[-1] if task.submissions else None
    return {"task": _task_to_response(task, last_submission)}


@router.post("/{task_id}/submit")
async def submit_task(
    task_id: int,
    body: SubmitTaskRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    task = task_orm.get_task(db, task_id=task_id, user_id=current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Задание не найдено")
    
    github_match = re.search(r'https?://github\.com/\S+', body.solution)
    repo_url = github_match.group(0) if github_match else None

    # Создаём сабмишн
    submission = task_orm.create_submission(
        db=db,
        task_id=task.id,
        user_id=current_user.id,
        solution_text=body.solution,
    )

    # Достаём requirements
    requirements = []
    if task.tech_stack and task.tech_stack.startswith("["):
        try:
            requirements = json.loads(task.tech_stack)
        except Exception:
            pass

    # Проверяем через AI
    try:
        ai_result = await review_solution(
            title=task.title or "",
            description=task.description,
            requirements=requirements,
            solution=body.solution,
            repo_url=repo_url,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка AI при проверке: {str(e)}")

    # Сохраняем результат
    task_orm.create_result(
        db=db,
        submission_id=submission.id,
        score=ai_result.get("score", 0),
        architecture_score=ai_result.get("architecture_score"),
        code_quality_score=ai_result.get("code_quality_score"),
        correctness_score=ai_result.get("correctness_score"),
        feedback=ai_result.get("feedback"),
        improvements=ai_result.get("improvements"),
    )

    # Перечитываем из БД чтобы получить результат через relationship
    db.refresh(submission)

    return {"task": _task_to_response(task, submission)}