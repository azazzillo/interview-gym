from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.user import UserCreate, UserLogin
from app.schemas.auth import TokenResponse
from app.orm import auth as user_crud
from app.services.hashing import Hasher
from app.services.auth import create_access_token, create_refresh_token

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse)
def register(data: UserCreate, db: Session = Depends(get_db)):
    existing_user = user_crud.get_user_by_email(db, data.email)

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    user = user_crud.create_user(db, data)

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        user=user
    )


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = user_crud.get_user_by_email(db, data.email)

    if not user or not Hasher.verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        user=user
    )