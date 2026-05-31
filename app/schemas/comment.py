# FastAPI
from pydantic import BaseModel
# Python
from datetime import datetime
# Local
from .user import UserShort


class CommentCreate(BaseModel):
    content: str


class CommentResponse(BaseModel):
    id: int
    content: str
    created_at: datetime

    user: UserShort

    class Config:
        from_attributes = True
        