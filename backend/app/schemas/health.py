from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(default="healthy", description="Current service health status")
    app_name: str = Field(default="ExplainMe", description="Application name")
    version: str = Field(default="1.0.0", description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Server UTC timestamp")
    services: Dict[str, Any] = Field(
        default_factory=dict,
        description="Health status of external services (PostgreSQL, Redis, Celery)",
    )
