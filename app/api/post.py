# Python
from typing import List, Optional
import os
import uuid
import shutil
# FastAPI
from fastapi import (
    APIRouter, Depends,UploadFile, 
    File, Form
)
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
# Local
from app.services.deps import get_current_user_optional, get_current_user
from app.schemas.post import PostResponse, PostCreate
from app.services.deps import get_current_user
from app.orm import post as post_orm
from app.db import get_db
from app.models import Post
from app.schemas.comment import CommentCreate, CommentResponse


router = APIRouter(prefix="/api/post", tags=["Post"])


@router.get("/", response_model=list[PostResponse])
def get_posts(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional)   # ← было без авторизации
):
    posts = post_orm.get_posts(db)
    result = []
    for post in posts:
        liked_by_me = False
        if current_user:
            liked_by_me = post_orm.is_liked(db, user_id=current_user.id, post_id=post.id)
        result.append({
            "id": post.id,
            "title": post.title,
            "caption": post.content,
            "image_url": post.image_url,
            "created_at": post.created_at,
            "author": {
                "id": post.user.id,
                "full_name": post.user.full_name,
                "avatar_url": post.user.avatar_url,
                "role": getattr(post.user, "role", None)
            },
            "comments": post.comments,
            "likes_count": len(post.likes),
            "liked_by_me": liked_by_me
        })
    return result


@router.post("/{post_id}/like")
def like_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    liked = post_orm.toggle_like(db, user_id=current_user.id, post_id=post_id)
    post = db.query(Post).filter_by(id=post_id).first()
    return {
        "liked": liked,
        "likes_count": len(post.likes)
    }


@router.post("/{post_id}/comment", response_model=CommentResponse)
def add_comment(
    post_id: int,
    body: CommentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    comment = post_orm.create_comment(
        db, user_id=current_user.id, post_id=post_id, caption=body.content
    )
    return {
        "id": comment.id,
        "content": comment.content,
        "created_at": comment.created_at,
        "user": {
            "id": current_user.id,
            "full_name": current_user.full_name,
            "avatar_url": current_user.avatar_url,
            "role": getattr(current_user, "role", None)
        }
    }

@router.post("/create", response_model=PostResponse)
async def create_post(
    caption: str = Form(...),
    title: str | None = Form(None),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    
    image_url = None

    if image:
        filename = f"{uuid.uuid4()}.jpg"

        upload_path = os.path.join(
            "uploads",
            filename
        )

        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(
                image.file,
                buffer
            )

        image_url = f"/uploads/{filename}"

    post = post_orm.create_post(
        db=db,
        user_id=current_user.id,
        title=title,
        caption=caption,
        image_url=image_url
    )

    return {
        "id": post.id,

        "title": post.title,

        "caption": post.content,

        "image_url": post.image_url,

        "created_at": post.created_at,

        "author": {
            "id": current_user.id,
            "full_name": current_user.full_name,
            "avatar_url": current_user.avatar_url,
            "role": getattr(current_user, "role", None)
        },

        "comments": [],

        "likes_count": 0,

        "liked_by_me": False
    }
