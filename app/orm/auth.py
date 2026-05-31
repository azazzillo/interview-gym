from sqlalchemy.orm import Session
from app.models import User
from app.schemas.user import UserCreate
from app.services.hashing import Hasher


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, data: UserCreate):
    user = User(
        full_name=data.full_name,
        email=data.email,
        password_hash=Hasher.get_password_hash(data.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user
