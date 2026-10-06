from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class JobResponse(BaseModel):
    id: str
    video_id: str
    status: str = Field(description="queued, downloading, transcribing, summarizing, indexing, completed, failed")
    progress_percent: int = Field(default=0, ge=0, le=100)
    current_step: str = Field(default="Job queued")
    source_used: Optional[str] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnalyzeVideoResponse(BaseModel):
    job_id: str
    video_id: str
    status: str = "queued"
    message: str = "Video analysis job has been queued successfully."
