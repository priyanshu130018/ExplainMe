import uuid
from typing import List, Optional
from sqlalchemy import String, Integer, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin

try:
    from pgvector.sqlalchemy import Vector
    HAS_PGVECTOR = True
except ImportError:
    HAS_PGVECTOR = False


class Transcript(Base, TimestampMixin):
    __tablename__ = "transcripts"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    video_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("videos.id", ondelete="CASCADE"), unique=True, index=True, nullable=False
    )
    full_text: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(16), default="en", nullable=False)
    source_type: Mapped[str] = mapped_column(String(32), default="captions", nullable=False)
    word_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    video: Mapped["Video"] = relationship("Video", back_populates="transcript")


class TranscriptChunk(Base, TimestampMixin):
    __tablename__ = "transcript_chunks"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    video_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("videos.id", ondelete="CASCADE"), index=True, nullable=False
    )
    chunk_index: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    start_time: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    end_time: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Store embedding as pgvector Vector (384-dim for all-MiniLM-L6-v2) or JSON fallback
    if HAS_PGVECTOR:
        embedding = mapped_column(Vector(384), nullable=True)
    else:
        embedding = mapped_column(JSON, nullable=True)

    # Relationships
    video: Mapped["Video"] = relationship("Video", back_populates="transcript_chunks")
