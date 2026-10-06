import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_router
from app.db.base import Base
from app.db.session import engine

# Import all models to ensure metadata registration
import app.models  # noqa: F401

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info(f"Starting {settings.APP_NAME} API in {settings.APP_ENV} mode...")
    
    # Auto-create tables on startup if not already created by Alembic
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database schema validated / created successfully.")
    except Exception as e:
        logger.warning(f"Database table initialization notice: {e}")

    yield
    logger.info("Shutting down ExplainMe API...")


app = FastAPI(
    title=settings.APP_NAME,
    description="ExplainMe API — AI-powered video understanding & educational tutoring.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include v1 API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["root"])
def root():
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "description": "AI-powered video understanding platform.",
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health",
    }
