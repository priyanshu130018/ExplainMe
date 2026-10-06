import logging
from datetime import datetime
from app.core.celery_app import celery_app
from app.db.session import SessionLocal
from app.models.job import AnalysisJob
from app.models.video import Video
from app.workflows.video_pipeline import video_analysis_pipeline

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="app.workers.video_tasks.process_video_analysis")
def process_video_analysis(self, job_id: str, video_id: str, url: str, language: str = "english"):
    """
    Background worker pipeline executing the LangGraph video intelligence workflow.
    """
    logger.info(f"[Worker] Starting analysis job {job_id} for video {video_id}")
    db = SessionLocal()
    try:
        video = db.query(Video).filter(Video.id == video_id).first()
        job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
        if not video or not job:
            logger.error(f"[Worker] Video {video_id} or Job {job_id} not found.")
            return

        initial_state = {
            "job_id": job_id,
            "video_id": video_id,
            "youtube_id": video.youtube_id,
            "url": url,
            "language": language,
            "title": video.title,
            "channel_name": video.channel_name,
            "duration_seconds": video.duration_seconds,
            "thumbnail_url": video.thumbnail_url,
            "view_count": video.view_count,
            "raw_chunks": [],
            "semantic_chunks": [],
            "full_transcript": "",
            "source_used": "captions",
            "quick_summary": "",
            "detailed_summary": "",
            "key_points": [],
            "keywords": [],
            "embeddings": [],
            "error": None,
        }

        # Run the LangGraph workflow
        final_state = video_analysis_pipeline.invoke(initial_state)

        if final_state.get("error"):
            raise ValueError(final_state["error"])

        logger.info(f"[Worker] Successfully completed job {job_id} for video {video_id}")

    except Exception as exc:
        logger.exception(f"[Worker] Pipeline execution failed for job {job_id}: {exc}")
        job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
        if job:
            job.status = "failed"
            job.error_message = str(exc)
            job.current_step = f"Failed: {str(exc)}"
            job.completed_at = datetime.utcnow()
            db.commit()
    finally:
        db.close()
