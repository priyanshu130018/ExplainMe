import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.video import Video
from app.models.job import AnalysisJob
from app.models.transcript import Transcript, TranscriptChunk
from app.models.summary import Summary
from app.models.keypoint import KeyPoint
from app.models.keyword import Keyword

client = TestClient(app)


def test_health_check_contract(db_session):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("healthy", "degraded")
    assert data["app_name"] == "ExplainMe"
    assert "services" in data


def test_analyze_video_endpoint_validation():
    # Invalid URL
    response = client.post(
        "/api/v1/videos/analyze",
        json={"url": "not-a-valid-url", "language": "english"},
    )
    assert response.status_code == 400
    assert "Invalid YouTube URL" in response.json()["detail"]


def test_analyze_video_endpoint_valid_contract(db_session):
    response = client.post(
        "/api/v1/videos/analyze",
        json={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "language": "english"},
    )
    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert "video_id" in data
    assert data["status"] == "queued"


def test_get_job_status_endpoint(db_session):
    video = Video(
        youtube_id="abc12345678",
        url="https://www.youtube.com/watch?v=abc12345678",
        title="Test Video",
    )
    db_session.add(video)
    db_session.flush()

    job = AnalysisJob(
        video_id=video.id,
        status="processing",
        progress_percent=45,
        current_step="Processing audio fallback",
    )
    db_session.add(job)
    db_session.commit()

    response = client.get(f"/api/v1/jobs/{job.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == job.id
    assert data["status"] == "processing"
    assert data["progress_percent"] == 45


def test_get_video_detail_endpoint(db_session):
    video = Video(
        youtube_id="xyz98765432",
        url="https://www.youtube.com/watch?v=xyz98765432",
        title="Deep Dive into Neural Networks",
        channel_name="AI Academy",
        duration_seconds=360,
    )
    db_session.add(video)
    db_session.flush()

    summary = Summary(
        video_id=video.id,
        quick_summary="A concise overview of backpropagation and loss functions.",
        detailed_summary="## 1. Backpropagation\nExplains gradient descent.",
        model_used="mistral-small-latest",
        language="en",
    )
    db_session.add(summary)

    point = KeyPoint(
        video_id=video.id,
        point_index=1,
        title="Gradient Descent",
        description="Core optimization technique.",
        timestamp_seconds=42.0,
    )
    db_session.add(point)

    kw = Keyword(
        video_id=video.id,
        keyword="Neural Networks",
        category="Concept",
        relevance_score=0.98,
    )
    db_session.add(kw)
    db_session.commit()

    response = client.get(f"/api/v1/videos/{video.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == video.id
    assert data["title"] == "Deep Dive into Neural Networks"
    assert data["summary"]["quick_summary"] == summary.quick_summary
    assert len(data["key_points"]) == 1
    assert data["key_points"][0]["title"] == "Gradient Descent"
    assert len(data["keywords"]) == 1


def test_get_video_transcript_and_summary_endpoints(db_session):
    video = Video(
        youtube_id="vid_trans_123",
        url="https://www.youtube.com/watch?v=vid_trans_123",
        title="Transcript Test Video",
    )
    db_session.add(video)
    db_session.flush()

    transcript = Transcript(
        video_id=video.id,
        full_text="Hello world this is a test transcript.",
        language="en",
        source_type="captions",
        word_count=7,
    )
    db_session.add(transcript)

    chunk = TranscriptChunk(
        video_id=video.id,
        chunk_index=0,
        start_time=0.0,
        end_time=5.0,
        text="Hello world this is a test transcript.",
        embedding=[0.0] * 384,
    )
    db_session.add(chunk)

    summary = Summary(
        video_id=video.id,
        quick_summary="Quick summary test.",
        detailed_summary="Detailed summary test.",
        model_used="mistral-small-latest",
        language="en",
    )
    db_session.add(summary)
    db_session.commit()

    # Test /transcript
    res_t = client.get(f"/api/v1/videos/{video.id}/transcript")
    assert res_t.status_code == 200
    data_t = res_t.json()
    assert data_t["full_text"] == transcript.full_text
    assert len(data_t["chunks"]) == 1

    # Test /summary
    res_s = client.get(f"/api/v1/videos/{video.id}/summary")
    assert res_s.status_code == 200
    data_s = res_s.json()
    assert data_s["quick_summary"] == summary.quick_summary


def test_ask_question_endpoint(db_session):
    video = Video(
        youtube_id="qa_test_video",
        url="https://www.youtube.com/watch?v=qa_test_video",
        title="Q&A Test Video",
    )
    db_session.add(video)
    db_session.flush()

    transcript = Transcript(
        video_id=video.id,
        full_text="Transformer models utilize self-attention mechanisms to weigh token relevance.",
        language="en",
        source_type="captions",
        word_count=10,
    )
    db_session.add(transcript)

    chunk = TranscriptChunk(
        video_id=video.id,
        chunk_index=0,
        start_time=15.0,
        end_time=30.0,
        text="Transformer models utilize self-attention mechanisms to weigh token relevance.",
        embedding=[0.05] * 384,
    )
    db_session.add(chunk)
    db_session.commit()

    response = client.post(
        f"/api/v1/videos/{video.id}/ask",
        json={"question": "What do transformer models utilize?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert data["question"] == "What do transformer models utilize?"
