from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TaskResultResponse(BaseModel):
    score: int
    architecture_score: Optional[int] = None
    code_quality_score: Optional[int] = None
    correctness_score: Optional[int] = None
    feedback: Optional[str] = None
    improvements: Optional[str] = None

    class Config:
        from_attributes = True


class TaskSubmissionResponse(BaseModel):
    id: int
    solution_text: Optional[str] = None
    repo_url: Optional[str] = None
    created_at: datetime
    result: Optional[TaskResultResponse] = None

    class Config:
        from_attributes = True


class TaskResponse(BaseModel):
    id: int
    title: Optional[str] = None
    description: str
    tech_stack: Optional[str] = None
    difficulty: Optional[str] = None
    time_limit: Optional[int] = None
    created_at: datetime

    # Вычисляемые поля для фронта
    vacancy: Optional[str] = None
    level: Optional[str] = None
    status: str = "pending"
    score: Optional[int] = None
    feedback: Optional[str] = None
    requirements: list[str] = []
    solution: Optional[str] = None

    class Config:
        from_attributes = True


class GenerateTaskRequest(BaseModel):
    vacancy: str
    level: str = "middle"
    topic: str = ""


class SubmitTaskRequest(BaseModel):
    solution: str
    notes: Optional[str] = None


class SubmitTaskResponse(BaseModel):
    task: TaskResponse