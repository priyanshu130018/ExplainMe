import asyncio
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.db.session import SessionLocal
from app.models.job import AnalysisJob
from app.schemas.job import JobResponse

router = APIRouter()


@router.get("/jobs/{job_id}", response_model=JobResponse, tags=["jobs"])
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """
    Retrieve current processing status and progress for a video analysis job.
    """
    job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis job '{job_id}' not found.",
        )
    return job


@router.get("/jobs/{job_id}/events", tags=["jobs"])
async def stream_job_events(job_id: str, request: Request):
    """
    Server-Sent Events (SSE) stream delivering real-time progress updates for a job.
    """
    async def event_generator():
        last_progress = -1
        last_step = ""
        last_status = ""

        for _ in range(300):  # Stream for up to 5 minutes
            if await request.is_disconnected():
                break

            db = SessionLocal()
            try:
                job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
                if not job:
                    yield f"event: error\ndata: {json.dumps({'error': 'Job not found'})}\n\n"
                    break

                # Send event if state changed or initially
                if (
                    job.progress_percent != last_progress
                    or job.current_step != last_step
                    or job.status != last_status
                ):
                    last_progress = job.progress_percent
                    last_step = job.current_step
                    last_status = job.status

                    event_data = {
                        "job_id": job.id,
                        "video_id": job.video_id,
                        "status": job.status,
                        "progress_percent": job.progress_percent,
                        "current_step": job.current_step,
                        "error_message": job.error_message,
                    }

                    yield f"event: job.progress\ndata: {json.dumps(event_data)}\n\n"

                if job.status in ("completed", "failed"):
                    event_type = "job.completed" if job.status == "completed" else "job.failed"
                    yield f"event: {event_type}\ndata: {json.dumps({'status': job.status})}\n\n"
                    break

            finally:
                db.close()

            await asyncio.sleep(1.0)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
