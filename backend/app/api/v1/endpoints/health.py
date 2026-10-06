from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.core.config import settings
from app.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["health"])
def check_health(db: Session = Depends(get_db)):
    """
    Health check endpoint to verify API server, PostgreSQL database, and Redis broker connectivity.
    """
    services_status = {}

    # Check Database
    try:
        db.execute(text("SELECT 1"))
        services_status["database"] = {"status": "healthy", "type": "PostgreSQL"}
    except Exception as e:
        services_status["database"] = {"status": "unhealthy", "error": str(e)}

    # Check Redis
    try:
        import redis
        r = redis.from_url(settings.REDIS_URL, socket_timeout=1.0)
        r.ping()
        services_status["redis"] = {"status": "healthy"}
    except Exception as e:
        services_status["redis"] = {"status": "unhealthy", "error": str(e)}

    overall_status = (
        "healthy"
        if all(s.get("status") == "healthy" for s in services_status.values())
        else "degraded"
    )

    return HealthResponse(
        status=overall_status,
        app_name=settings.APP_NAME,
        version="1.0.0",
        timestamp=datetime.utcnow(),
        services=services_status,
    )
