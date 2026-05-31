# Python
from datetime import datetime
from typing import Optional
# Pydantic
from pydantic import(
    BaseModel, EmailStr, Field, model_validator, ConfigDict
)
# Local
from .user import UserShort
from .comment import CommentResponse


class PostCreate(BaseModel):
    title: Optional[str]
    caption: str
    image_url: Optional[str]


class PostResponse(BaseModel):
    id: int

    title: Optional[str]
    caption: str

    image_url: Optional[str]

    created_at: datetime

    author: UserShort

    comments: list[CommentResponse]

    likes_count: int
    liked_by_me: bool

    class Config:
        from_attributes = True