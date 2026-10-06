from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "explainme_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.workers.video_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per task
    task_soft_time_limit=3000,
    worker_prefetch_multiplier=1,
    broker_connection_timeout=2.0,
    broker_connection_retry_on_startup=False,
    redis_socket_connect_timeout=2.0,
    redis_socket_timeout=2.0,
)
