from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserShort(BaseModel):
    id: int
    full_name: str | None = None
    avatar_url: str | None = None
    role: str | None = None

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    avatar_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True