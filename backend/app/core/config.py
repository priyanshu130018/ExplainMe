import os
from typing import List, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "ExplainMe"
    APP_ENV: str = "development"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    PORT: int = 8000
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:80",
        "http://127.0.0.1:80",
        "*"
    ]

    # Database (Neon PostgreSQL)
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/explainme"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800

    # Redis & Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # AI & Speech Models
    MISTRAL_API_KEY: Optional[str] = None
    MISTRAL_MODEL: str = "mistral-small-latest"
    SARVAM_API_KEY: Optional[str] = None
    WHISPER_MODEL: str = "base"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    ENABLE_PGVECTOR: bool = True

    # Security
    AUTH_SECRET: str = "explainme_super_secret_dev_key_2026"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_database_url(cls, v: Optional[str]) -> str:
        if not v:
            return "postgresql+psycopg://postgres:postgres@localhost:5432/explainme"
        # Normalize standard postgres URLs to psycopg3 driver for SQLAlchemy 2
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+psycopg://", 1)
        if v.startswith("postgresql://") and not v.startswith("postgresql+"):
            return v.replace("postgresql://", "postgresql+psycopg://", 1)
        return v

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
