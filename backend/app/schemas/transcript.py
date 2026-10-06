from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class TranscriptChunkSchema(BaseModel):
    id: str
    chunk_index: int
    start_time: float
    end_time: float
    text: str

    model_config = ConfigDict(from_attributes=True)


class TranscriptResponse(BaseModel):
    id: str
    video_id: str
    full_text: str
    language: str
    source_type: str
    word_count: int
    chunks: List[TranscriptChunkSchema] = []

    model_config = ConfigDict(from_attributes=True)
