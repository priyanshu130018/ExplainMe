import pytest
from app.services.vector_service import VectorService
from app.services.llm_provider import MistralLLMProvider
from app.services.rag_service import RAGService
from app.models.video import Video
from app.models.transcript import Transcript, TranscriptChunk


def test_vector_service_segmentation():
    raw_chunks = [
        {"chunk_index": 0, "start_time": 0.0, "end_time": 10.0, "text": "Welcome to this introductory lecture on modern database architecture."},
        {"chunk_index": 1, "start_time": 10.0, "end_time": 20.0, "text": "We will explore how storage engines and query optimizers interact under high concurrency."},
        {"chunk_index": 2, "start_time": 20.0, "end_time": 35.0, "text": "Vector databases represent dense high-dimensional embeddings for semantic search."},
    ]

    semantic = VectorService.segment_transcript_into_semantic_chunks(raw_chunks, target_word_count=15)
    assert len(semantic) >= 1
    assert "start_time" in semantic[0]
    assert "end_time" in semantic[0]
    assert "text" in semantic[0]


def test_llm_provider_quick_explanation_fallback():
    provider = MistralLLMProvider(api_key=None)
    transcript = "This lecture discusses vector indexes, similarity search, and how retrieval augmented generation works in production."
    summary = provider.generate_quick_explanation(transcript, "Vector Databases Explained")
    assert len(summary) > 20
    assert "Vector Databases" in summary or "principles" in summary


def test_llm_provider_key_points_extraction():
    provider = MistralLLMProvider(api_key=None)
    chunks = [{"start_time": 0.0, "end_time": 60.0, "text": "Overview of relational and vector storage"}]
    points = provider.extract_key_points("Relational vs vector storage tradeoffs", chunks)
    assert isinstance(points, list)
    assert len(points) >= 1
    assert "title" in points[0]
    assert "description" in points[0]


def test_rag_anti_hallucination_empty_video(db_session):
    res = RAGService.answer_question_grounded(
        db=db_session,
        video_id="non-existent-video-uuid",
        question="What is the meaning of life?",
    )
    assert "couldn't find enough information" in res["answer"].lower()
    assert len(res["sources"]) == 0


def test_rag_grounded_answer_with_context(db_session):
    # Seed test video and transcript chunks
    video = Video(
        youtube_id="dQw4w9WgXcQ",
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        title="Vector Search Explained",
    )
    db_session.add(video)
    db_session.flush()

    chunk1 = TranscriptChunk(
        video_id=video.id,
        chunk_index=0,
        start_time=12.0,
        end_time=30.0,
        text="Vector databases store high dimensional embeddings and use cosine similarity to find semantic neighbors.",
        embedding=[0.1] * 384,
    )
    db_session.add(chunk1)
    db_session.commit()

    res = RAGService.answer_question_grounded(
        db=db_session,
        video_id=video.id,
        question="What do vector databases store?",
    )

    assert "answer" in res
    assert len(res["sources"]) > 0
    assert res["sources"][0]["start_time"] == 12.0
