from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.summary import SummaryResponse, KeyPointSchema, KeywordSchema
from app.schemas.job import JobResponse, AnalyzeVideoResponse


class AnalyzeVideoRequest(BaseModel):
    url: str = Field(..., description="YouTube video URL to analyze")
    language: str = Field(default="english", description="Preferred language (english / hinglish / auto)")


class VideoBase(BaseModel):
    youtube_id: str
    url: str
    title: str
    channel_name: Optional[str] = None
    duration_seconds: Optional[int] = None
    thumbnail_url: Optional[str] = None
    view_count: Optional[int] = None
    language_code: str = "en"


class VideoListItem(VideoBase):
    id: str
    created_at: datetime
    updated_at: datetime
    latest_job_status: Optional[str] = None
    quick_summary_preview: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class VideoDetailResponse(VideoBase):
    id: str
    created_at: datetime
    updated_at: datetime
    summary: Optional[SummaryResponse] = None
    key_points: List[KeyPointSchema] = []
    keywords: List[KeywordSchema] = []
    transcript_preview: Optional[str] = None
    transcript_word_count: Optional[int] = None
    latest_job: Optional[JobResponse] = None

    model_config = ConfigDict(from_attributes=True)


class VideoListResponse(BaseModel):
    items: List[VideoListItem]
    total: int
    page: int = 1
    page_size: int = 20
