from sqlalchemy.orm import Session
from app.models import Task, TaskSubmission, TaskResult


def get_tasks(db: Session, user_id: int, page: int = 1, limit: int = 10):
    offset = (page - 1) * limit
    return (
        db.query(Task)
        .filter(Task.user_id == user_id)
        .order_by(Task.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_task(db: Session, task_id: int, user_id: int):
    return (
        db.query(Task)
        .filter(Task.id == task_id, Task.user_id == user_id)
        .first()
    )


def create_task(db: Session, user_id: int, title: str, description: str,
                tech_stack: str = None, difficulty: str = None, time_limit: int = None) -> Task:
    task = Task(
        user_id=user_id,
        title=title,
        description=description,
        tech_stack=tech_stack,
        difficulty=difficulty,
        time_limit=time_limit,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def create_submission(db: Session, task_id: int, user_id: int,
                      solution_text: str = None, repo_url: str = None) -> TaskSubmission:
    submission = TaskSubmission(
        task_id=task_id,
        user_id=user_id,
        solution_text=solution_text,
        repo_url=repo_url,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


def create_result(db: Session, submission_id: int, score: int, architecture_score: int,
                  code_quality_score: int, correctness_score: int,
                  feedback: str, improvements: str) -> TaskResult:
    result = TaskResult(
        submission_id=submission_id,
        score=score,
        architecture_score=architecture_score,
        code_quality_score=code_quality_score,
        correctness_score=correctness_score,
        feedback=feedback,
        improvements=improvements,
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result