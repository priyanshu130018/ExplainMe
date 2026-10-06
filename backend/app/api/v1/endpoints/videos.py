from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.api.deps import get_db
from app.models.video import Video
from app.models.job import AnalysisJob
from app.models.transcript import Transcript, TranscriptChunk
from app.models.summary import Summary
from app.models.question import QuestionAnswer
from app.schemas.video import (
    AnalyzeVideoRequest,
    AnalyzeVideoResponse,
    VideoDetailResponse,
    VideoListItem,
    VideoListResponse,
)
from app.schemas.transcript import TranscriptResponse
from app.schemas.summary import SummaryResponse
from app.schemas.question import AskQuestionRequest, QuestionAnswerResponse
from app.services.youtube_service import YouTubeService
from app.services.rag_service import RAGService
from app.workers.video_tasks import process_video_analysis

router = APIRouter()


@router.post(
    "/videos/analyze",
    response_model=AnalyzeVideoResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["videos"],
)
def submit_video_analysis(
    payload: AnalyzeVideoRequest,
    db: Session = Depends(get_db),
):
    """
    Submit a YouTube URL for analysis.
    Validates URL, provisions/updates video & job records, enqueues background Celery worker,
    and returns job_id immediately.
    """
    url = payload.url.strip()
    if not YouTubeService.is_valid_url(url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid YouTube URL. Please provide a valid YouTube video link.",
        )

    youtube_id = YouTubeService.extract_video_id(url)
    if not youtube_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not parse YouTube Video ID from provided URL.",
        )

    # Find or create Video record
    video = db.query(Video).filter(Video.youtube_id == youtube_id).first()
    if not video:
        video = Video(
            youtube_id=youtube_id,
            url=f"https://www.youtube.com/watch?v={youtube_id}",
            title=f"YouTube Video ({youtube_id})",
            thumbnail_url=f"https://img.youtube.com/vi/{youtube_id}/maxresdefault.jpg",
        )
        db.add(video)
        db.flush()

    # Create new AnalysisJob record
    job = AnalysisJob(
        video_id=video.id,
        status="queued",
        progress_percent=0,
        current_step="Job queued for processing",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Enqueue Celery Task
    try:
        task = process_video_analysis.delay(
            job_id=job.id,
            video_id=video.id,
            url=video.url,
            language=payload.language,
        )
        job.celery_task_id = task.id
        db.commit()
    except Exception as e:
        job.current_step = f"Queued (celery worker sync fallback: {str(e)})"
        db.commit()

    return AnalyzeVideoResponse(
        job_id=job.id,
        video_id=video.id,
        status="queued",
        message="Video analysis job has been queued successfully.",
    )


@router.get("/videos", response_model=VideoListResponse, tags=["videos"])
def list_videos(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    List all processed / analyzed videos, ordered by recent creation.
    """
    total = db.query(Video).count()
    offset = (page - 1) * page_size

    videos = (
        db.query(Video)
        .order_by(desc(Video.created_at))
        .offset(offset)
        .limit(page_size)
        .all()
    )

    items = []
    for v in videos:
        latest_job = (
            db.query(AnalysisJob)
            .filter(AnalysisJob.video_id == v.id)
            .order_by(desc(AnalysisJob.created_at))
            .first()
        )
        summary = db.query(Summary).filter(Summary.video_id == v.id).first()
        
        preview = None
        if summary and summary.quick_summary:
            preview = (
                summary.quick_summary[:160] + "..."
                if len(summary.quick_summary) > 160
                else summary.quick_summary
            )

        items.append(
            VideoListItem(
                id=v.id,
                youtube_id=v.youtube_id,
                url=v.url,
                title=v.title,
                channel_name=v.channel_name,
                duration_seconds=v.duration_seconds,
                thumbnail_url=v.thumbnail_url,
                view_count=v.view_count,
                language_code=v.language_code,
                created_at=v.created_at,
                updated_at=v.updated_at,
                latest_job_status=latest_job.status if latest_job else None,
                quick_summary_preview=preview,
            )
        )

    return VideoListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/videos/{video_id}", response_model=VideoDetailResponse, tags=["videos"])
def get_video_detail(video_id: str, db: Session = Depends(get_db)):
    """
    Get detailed analysis results for a video (quick summary, detailed explanation,
    key points, keywords, and latest job status).
    """
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        video = db.query(Video).filter(Video.youtube_id == video_id).first()

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video '{video_id}' not found.",
        )

    latest_job = (
        db.query(AnalysisJob)
        .filter(AnalysisJob.video_id == video.id)
        .order_by(desc(AnalysisJob.created_at))
        .first()
    )
    
    transcript = db.query(Transcript).filter(Transcript.video_id == video.id).first()
    transcript_preview = None
    transcript_word_count = None
    if transcript:
        transcript_preview = (
            transcript.full_text[:1000] + "..."
            if len(transcript.full_text) > 1000
            else transcript.full_text
        )
        transcript_word_count = transcript.word_count

    return VideoDetailResponse(
        id=video.id,
        youtube_id=video.youtube_id,
        url=video.url,
        title=video.title,
        channel_name=video.channel_name,
        duration_seconds=video.duration_seconds,
        thumbnail_url=video.thumbnail_url,
        view_count=video.view_count,
        language_code=video.language_code,
        created_at=video.created_at,
        updated_at=video.updated_at,
        summary=video.summary,
        key_points=video.key_points or [],
        keywords=video.keywords or [],
        transcript_preview=transcript_preview,
        transcript_word_count=transcript_word_count,
        latest_job=latest_job,
    )


@router.get("/videos/{video_id}/transcript", response_model=TranscriptResponse, tags=["videos"])
def get_video_transcript(video_id: str, db: Session = Depends(get_db)):
    """
    Get full transcript and timestamped chunks for an analyzed video.
    """
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found.")

    transcript = db.query(Transcript).filter(Transcript.video_id == video.id).first()
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not available for this video.")

    chunks = (
        db.query(TranscriptChunk)
        .filter(TranscriptChunk.video_id == video.id)
        .order_by(TranscriptChunk.chunk_index)
        .all()
    )

    return TranscriptResponse(
        id=transcript.id,
        video_id=video.id,
        full_text=transcript.full_text,
        language=transcript.language,
        source_type=transcript.source_type,
        word_count=transcript.word_count,
        chunks=chunks,
    )


@router.get("/videos/{video_id}/summary", response_model=SummaryResponse, tags=["videos"])
def get_video_summary(video_id: str, db: Session = Depends(get_db)):
    """
    Get quick and detailed summary for an analyzed video.
    """
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found.")

    summary = db.query(Summary).filter(Summary.video_id == video.id).first()
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not available for this video.")

    return summary


@router.post("/videos/{video_id}/ask", response_model=QuestionAnswerResponse, tags=["videos"])
def ask_video_question(
    video_id: str,
    payload: AskQuestionRequest,
    db: Session = Depends(get_db),
):
    """
    Ask a question grounded strictly in the video transcript via RAG vector search.
    """
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        video = db.query(Video).filter(Video.youtube_id == video_id).first()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found.")

    res = RAGService.answer_question_grounded(
        db=db,
        video_id=video.id,
        question=payload.question,
    )

    qa = QuestionAnswer(
        video_id=video.id,
        question=payload.question,
        answer=res["answer"],
        sources=res.get("sources"),
    )
    db.add(qa)
    db.commit()
    db.refresh(qa)

    return qa
