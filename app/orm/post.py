from sqlalchemy.orm import Session
# Local
from app.models import Post, PostLike, Comment


def get_posts(db: Session):
    return db.query(Post).all()


def create_post(db, user_id, title, caption, image_url):
    post = Post(
        user_id=user_id,
        title=title,
        content=caption,
        image_url=image_url
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    return post


def toggle_like(db: Session, user_id: int, post_id: int):
    like = db.query(PostLike).filter_by(
        user_id=user_id,
        post_id=post_id
    ).first()

    if like:
        db.delete(like)
        db.commit()
        return False

    new_like = PostLike(
        user_id=user_id,
        post_id=post_id
    )

    db.add(new_like)
    db.commit()
    return True


def create_comment(db: Session, user_id: int, post_id: int, caption: str):
    comment = Comment(
        user_id=user_id,
        post_id=post_id,
        content=caption
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment

def is_liked(db: Session, user_id: int, post_id: int) -> bool:
    return db.query(PostLike).filter_by(
        user_id=user_id,
        post_id=post_id
    ).first() is not None