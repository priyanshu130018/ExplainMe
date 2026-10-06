from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class KeyPointSchema(BaseModel):
    id: Optional[str] = None
    point_index: int
    title: str
    description: str
    timestamp_seconds: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class KeywordSchema(BaseModel):
    id: Optional[str] = None
    keyword: str
    category: Optional[str] = None
    relevance_score: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class SummaryResponse(BaseModel):
    id: str
    video_id: str
    quick_summary: str
    detailed_summary: str
    model_used: str
    language: str

    model_config = ConfigDict(from_attributes=True)
