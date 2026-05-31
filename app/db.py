# SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
# Python
import os
from dotenv import load_dotenv
# Local
import app.models


load_dotenv()

DATABASE_URL = os.getenv("DB_URL")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=15,
    max_overflow=10,
    pool_timeout=30,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

