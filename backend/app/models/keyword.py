import uuid
from typing import Optional
from sqlalchemy import String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class Keyword(Base, TimestampMixin):
    __tablename__ = "keywords"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    video_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("videos.id", ondelete="CASCADE"), index=True, nullable=False
    )
    keyword: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    relevance_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationships
    video: Mapped["Video"] = relationship("Video", back_populates="keywords")
