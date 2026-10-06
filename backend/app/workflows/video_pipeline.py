import logging
from datetime import datetime
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from app.db.session import SessionLocal
from app.models.job import AnalysisJob
from app.models.video import Video
from app.models.transcript import Transcript, TranscriptChunk
from app.models.summary import Summary
from app.models.keypoint import KeyPoint
from app.models.keyword import Keyword
from app.services.youtube_service import YouTubeService
from app.services.transcription_service import TranscriptionService
from app.services.llm_provider import MistralLLMProvider
from app.services.vector_service import VectorService

logger = logging.getLogger(__name__)


class PipelineState(TypedDict):
    job_id: str
    video_id: str
    youtube_id: str
    url: str
    language: str
    title: str
    channel_name: Optional[str]
    duration_seconds: Optional[int]
    thumbnail_url: Optional[str]
    view_count: Optional[int]
    raw_chunks: List[Dict[str, Any]]
    semantic_chunks: List[Dict[str, Any]]
    full_transcript: str
    source_used: str
    quick_summary: str
    detailed_summary: str
    key_points: List[Dict[str, Any]]
    keywords: List[Dict[str, Any]]
    embeddings: List[List[float]]
    error: Optional[str]


def _update_job_progress(job_id: str, progress: int, step_desc: str, status: str = "processing"):
    """Update job progress and state in PostgreSQL."""
    db = SessionLocal()
    try:
        job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
        if job:
            job.status = status
            job.progress_percent = progress
            job.current_step = step_desc
            if status == "completed":
                job.completed_at = datetime.utcnow()
            db.commit()
    except Exception as e:
        db.rollback()
        logger.warning(f"[Pipeline] Progress update failed for job {job_id}: {e}")
    finally:
        db.close()


# ── Workflow Node Definitions ─────────────────────────────────────────────────

def node_fetch_metadata(state: PipelineState) -> PipelineState:
    logger.info(f"[Pipeline] Step 1: Fetching metadata for {state['youtube_id']}")
    _update_job_progress(state["job_id"], 15, "Fetching video metadata and details...")

    meta = YouTubeService.fetch_metadata(state["url"], state["youtube_id"])
    return {
        **state,
        "title": meta.get("title", state["title"]),
        "channel_name": meta.get("channel_name"),
        "duration_seconds": meta.get("duration_seconds"),
        "thumbnail_url": meta.get("thumbnail_url"),
        "view_count": meta.get("view_count"),
    }


def node_retrieve_captions(state: PipelineState) -> PipelineState:
    logger.info(f"[Pipeline] Step 2: Attempting captions fast-path for {state['youtube_id']}")
    _update_job_progress(state["job_id"], 30, "Checking for native YouTube captions...")

    transcript_data = YouTubeService.get_captions_transcript(state["youtube_id"])
    if transcript_data and transcript_data.get("full_text"):
        return {
            **state,
            "full_transcript": transcript_data["full_text"],
            "raw_chunks": transcript_data.get("chunks", []),
            "source_used": "captions",
        }

    return {
        **state,
        "source_used": "none",
    }


def condition_captions_available(state: PipelineState) -> str:
    """Branch condition: captions available vs audio fallback STT."""
    if state.get("full_transcript") and state.get("source_used") == "captions":
        return "segment_transcript"
    return "audio_fallback_stt"


def node_audio_fallback_stt(state: PipelineState) -> PipelineState:
    logger.info(f"[Pipeline] Step 2b: Running audio fallback STT for {state['youtube_id']}")
    _update_job_progress(
        state["job_id"],
        40,
        "Captions unavailable. Downloading audio and running speech-to-text..."
    )

    try:
        stt_result = TranscriptionService.download_audio_and_transcribe(
            url=state["url"],
            video_id=state["youtube_id"],
            language=state.get("language", "english"),
        )
        if not stt_result or not stt_result.get("full_text"):
            raise ValueError("No speech could be extracted from this video.")

        return {
            **state,
            "full_transcript": stt_result["full_text"],
            "raw_chunks": stt_result.get("chunks", []),
            "source_used": stt_result.get("source_type", "audio_stt"),
        }
    except Exception as exc:
        logger.error(f"[Pipeline] Audio STT failed: {exc}")
        return {
            **state,
            "error": f"Audio transcription failed: {str(exc)}",
        }


def node_segment_transcript(state: PipelineState) -> PipelineState:
    logger.info("[Pipeline] Step 3: Segmenting and normalizing transcript chunks")
    _update_job_progress(state["job_id"], 50, "Normalizing transcript and timestamps...")

    raw_chunks = state.get("raw_chunks", [])
    if not raw_chunks and state.get("full_transcript"):
        raw_chunks = [{
            "chunk_index": 0,
            "start_time": 0.0,
            "end_time": float(state.get("duration_seconds") or 60.0),
            "text": state["full_transcript"],
        }]

    semantic_chunks = VectorService.segment_transcript_into_semantic_chunks(raw_chunks)
    return {
        **state,
        "semantic_chunks": semantic_chunks,
    }


def node_generate_explanations(state: PipelineState) -> PipelineState:
    logger.info("[Pipeline] Step 4: Generating quick and detailed explanations with AI")
    _update_job_progress(state["job_id"], 65, "Generating quick explanation & chapter deep dive...")

    llm = MistralLLMProvider()
    transcript_text = state["full_transcript"]
    semantic_chunks = state.get("semantic_chunks", [])

    quick_summary = llm.generate_quick_explanation(transcript_text, state["title"])
    detailed_summary = llm.generate_detailed_explanation(transcript_text, semantic_chunks)

    return {
        **state,
        "quick_summary": quick_summary,
        "detailed_summary": detailed_summary,
    }


def node_extract_insights(state: PipelineState) -> PipelineState:
    logger.info("[Pipeline] Step 5: Extracting key points and keywords")
    _update_job_progress(state["job_id"], 80, "Extracting actionable key takeaways and topic tags...")

    llm = MistralLLMProvider()
    transcript_text = state["full_transcript"]
    semantic_chunks = state.get("semantic_chunks", [])

    key_points = llm.extract_key_points(transcript_text, semantic_chunks)
    keywords = llm.extract_keywords(transcript_text)

    return {
        **state,
        "key_points": key_points,
        "keywords": keywords,
    }


def node_create_embeddings(state: PipelineState) -> PipelineState:
    logger.info("[Pipeline] Step 6: Generating pgvector embeddings for RAG")
    _update_job_progress(state["job_id"], 90, "Indexing vector knowledge base for Q&A...")

    semantic_chunks = state.get("semantic_chunks", [])
    embeddings = VectorService.generate_embeddings_for_chunks(semantic_chunks)

    return {
        **state,
        "embeddings": embeddings,
    }


def node_persist_results(state: PipelineState) -> PipelineState:
    logger.info("[Pipeline] Step 7: Persisting all results into PostgreSQL")
    _update_job_progress(state["job_id"], 95, "Finalizing and storing analysis...")

    db = SessionLocal()
    try:
        video = db.query(Video).filter(Video.id == state["video_id"]).first()
        if video:
            video.title = state["title"]
            video.channel_name = state["channel_name"]
            video.duration_seconds = state["duration_seconds"]
            video.thumbnail_url = state["thumbnail_url"]
            video.view_count = state["view_count"]

            # Store Transcript
            existing_t = db.query(Transcript).filter(Transcript.video_id == video.id).first()
            if not existing_t:
                existing_t = Transcript(
                    video_id=video.id,
                    full_text=state["full_transcript"],
                    language=state["language"],
                    source_type=state["source_used"],
                    word_count=len(state["full_transcript"].split()),
                )
                db.add(existing_t)
            else:
                existing_t.full_text = state["full_transcript"]
                existing_t.source_type = state["source_used"]
                existing_t.word_count = len(state["full_transcript"].split())

            # Store Transcript Chunks with Embeddings
            db.query(TranscriptChunk).filter(TranscriptChunk.video_id == video.id).delete()
            chunks = state.get("semantic_chunks", [])
            embs = state.get("embeddings", [])
            for idx, chk in enumerate(chunks):
                emb = embs[idx] if idx < len(embs) else None
                db.add(
                    TranscriptChunk(
                        video_id=video.id,
                        chunk_index=chk["chunk_index"],
                        start_time=chk["start_time"],
                        end_time=chk["end_time"],
                        text=chk["text"],
                        embedding=emb,
                    )
                )

            # Store Summary
            existing_s = db.query(Summary).filter(Summary.video_id == video.id).first()
            if not existing_s:
                db.add(
                    Summary(
                        video_id=video.id,
                        quick_summary=state["quick_summary"],
                        detailed_summary=state["detailed_summary"],
                        model_used="mistral-small-latest",
                        language=state["language"],
                    )
                )
            else:
                existing_s.quick_summary = state["quick_summary"]
                existing_s.detailed_summary = state["detailed_summary"]

            # Store Key Points
            db.query(KeyPoint).filter(KeyPoint.video_id == video.id).delete()
            for pt in state.get("key_points", []):
                db.add(
                    KeyPoint(
                        video_id=video.id,
                        point_index=pt.get("point_index", 1),
                        title=pt.get("title", "Key Takeaway"),
                        description=pt.get("description", ""),
                        timestamp_seconds=pt.get("timestamp_seconds"),
                    )
                )

            # Store Keywords
            db.query(Keyword).filter(Keyword.video_id == video.id).delete()
            for kw in state.get("keywords", []):
                db.add(
                    Keyword(
                        video_id=video.id,
                        keyword=kw.get("keyword", ""),
                        category=kw.get("category"),
                        relevance_score=kw.get("relevance_score"),
                    )
                )

            # Mark Job as completed
            job = db.query(AnalysisJob).filter(AnalysisJob.id == state["job_id"]).first()
            if job:
                job.status = "completed"
                job.progress_percent = 100
                job.current_step = "Analysis complete!"
                job.source_used = state["source_used"]
                job.completed_at = datetime.utcnow()

            db.commit()

    except Exception as exc:
        db.rollback()
        logger.error(f"[Pipeline] Persistence failed: {exc}")
        raise
    finally:
        db.close()

    return state


# ── Build LangGraph Pipeline ──────────────────────────────────────────────────

def build_video_analysis_pipeline():
    workflow = StateGraph(PipelineState)

    workflow.add_node("fetch_metadata", node_fetch_metadata)
    workflow.add_node("retrieve_captions", node_retrieve_captions)
    workflow.add_node("audio_fallback_stt", node_audio_fallback_stt)
    workflow.add_node("segment_transcript", node_segment_transcript)
    workflow.add_node("generate_explanations", node_generate_explanations)
    workflow.add_node("extract_insights", node_extract_insights)
    workflow.add_node("create_embeddings", node_create_embeddings)
    workflow.add_node("persist_results", node_persist_results)

    workflow.set_entry_point("fetch_metadata")
    workflow.add_edge("fetch_metadata", "retrieve_captions")

    workflow.add_conditional_edges(
        "retrieve_captions",
        condition_captions_available,
        {
            "segment_transcript": "segment_transcript",
            "audio_fallback_stt": "audio_fallback_stt",
        },
    )

    workflow.add_edge("audio_fallback_stt", "segment_transcript")
    workflow.add_edge("segment_transcript", "generate_explanations")
    workflow.add_edge("generate_explanations", "extract_insights")
    workflow.add_edge("extract_insights", "create_embeddings")
    workflow.add_edge("create_embeddings", "persist_results")
    workflow.add_edge("persist_results", END)

    return workflow.compile()


video_analysis_pipeline = build_video_analysis_pipeline()
