from fastapi import APIRouter
from app.api.v1.endpoints import health, jobs, videos

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(videos.router)
api_router.include_router(jobs.router)
