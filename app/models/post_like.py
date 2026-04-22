# SQLAlchemy
from sqlalchemy import Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
# Python
from datetime import datetime
# Local
from app.models.base import Base


class PostLike(Base):
    __tablename__ = "post_like"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id"),
        nullable=False
    )

    post_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("post.id"),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    # 🔥 чтобы нельзя было лайкнуть дважды
    __table_args__ = (
        UniqueConstraint("user_id", "post_id", name="unique_user_post_like"),
    )

    # связи
    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")