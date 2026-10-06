from typing import Generator
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

# If running in pytest or DATABASE_URL explicitly set to sqlite
db_url = settings.DATABASE_URL
if os.getenv("PYTEST_CURRENT_TEST") or os.getenv("TESTING") == "true":
    db_url = "sqlite:///:memory:"

connect_args = {}
engine_kwargs = {
    "pool_pre_ping": True,
    "echo": False,
}

if db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False
    engine_kwargs["connect_args"] = connect_args
else:
    # PostgreSQL / Neon settings
    connect_args["connect_timeout"] = 3
    engine_kwargs["connect_args"] = connect_args
    engine_kwargs["pool_size"] = settings.DB_POOL_SIZE
    engine_kwargs["max_overflow"] = settings.DB_MAX_OVERFLOW
    engine_kwargs["pool_recycle"] = settings.DB_POOL_RECYCLE
    engine_kwargs["pool_timeout"] = 5

engine = create_engine(db_url, **engine_kwargs)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency yielding a SQLAlchemy session.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
