from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class AskQuestionRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=1000, description="Question about the video content")


class QuestionAnswerResponse(BaseModel):
    id: str
    video_id: str
    question: str
    answer: str
    sources: Optional[Any] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
