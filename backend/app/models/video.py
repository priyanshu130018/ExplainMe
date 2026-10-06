import uuid
from typing import List, Optional
from sqlalchemy import String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class Video(Base, TimestampMixin):
    __tablename__ = "videos"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    youtube_id: Mapped[str] = mapped_column(
        String(32), unique=True, index=True, nullable=False
    )
    url: Mapped[str] = mapped_column(String(512), nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False, default="Untitled Video")
    channel_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    view_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    language_code: Mapped[str] = mapped_column(String(16), default="en", nullable=False)

    # Relationships
    jobs: Mapped[List["AnalysisJob"]] = relationship(
        "AnalysisJob", back_populates="video", cascade="all, delete-orphan"
    )
    transcript: Mapped[Optional["Transcript"]] = relationship(
        "Transcript", back_populates="video", uselist=False, cascade="all, delete-orphan"
    )
    transcript_chunks: Mapped[List["TranscriptChunk"]] = relationship(
        "TranscriptChunk", back_populates="video", cascade="all, delete-orphan"
    )
    summary: Mapped[Optional["Summary"]] = relationship(
        "Summary", back_populates="video", uselist=False, cascade="all, delete-orphan"
    )
    key_points: Mapped[List["KeyPoint"]] = relationship(
        "KeyPoint", back_populates="video", cascade="all, delete-orphan", order_by="KeyPoint.point_index"
    )
    keywords: Mapped[List["Keyword"]] = relationship(
        "Keyword", back_populates="video", cascade="all, delete-orphan"
    )
    questions: Mapped[List["QuestionAnswer"]] = relationship(
        "QuestionAnswer", back_populates="video", cascade="all, delete-orphan"
    )
