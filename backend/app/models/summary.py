import uuid
from typing import Optional
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class Summary(Base, TimestampMixin):
    __tablename__ = "summaries"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    video_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("videos.id", ondelete="CASCADE"), unique=True, index=True, nullable=False
    )
    quick_summary: Mapped[str] = mapped_column(Text, nullable=False)
    detailed_summary: Mapped[str] = mapped_column(Text, nullable=False)
    model_used: Mapped[str] = mapped_column(String(64), default="mistral-small-latest", nullable=False)
    language: Mapped[str] = mapped_column(String(16), default="en", nullable=False)

    # Relationships
    video: Mapped["Video"] = relationship("Video", back_populates="summary")
