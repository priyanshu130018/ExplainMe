# API & Backend Architecture Design

ExplainMe's backend is built using **Python 3.12+**, **FastAPI**, **SQLAlchemy 2**, **Pydantic v2**, and **Celery** with **Redis**.

---

## 🏛️ Architecture & Layer Separation

```text
HTTP Client (React / Third-party)
        │
        ▼
┌──────────────────────────────────────┐
│       FastAPI Web Application        │
│  - Middleware (CORS, Error Handlers) │
│  - Dependency Injection (DB Session) │
│  - Pydantic v2 Input/Output Schemas  │
└──────────────────┬───────────────────┘
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
┌──────────────────┐  ┌──────────────────┐
│  Service Layer   │  │   Celery Queue   │
│ - YouTubeService │  │  (Redis Broker)  │
│ - AudioService   │  └────────┬─────────┘
│ - LLMProvider    │           │
│ - VectorService  │           ▼
│ - RAGService     │  ┌──────────────────┐
└────────┬─────────┘  │  Celery Worker   │
         │            │  - LangGraph     │
         ▼            │    Pipeline      │
┌──────────────────┐  └────────┬─────────┘
│ SQLAlchemy 2 ORM │           │
└────────┬─────────┘           │
         ▼                     ▼
┌────────────────────────────────────────┐
│      Neon PostgreSQL + pgvector        │
└────────────────────────────────────────┘
```

---

## 📦 Service Layer Responsibilities

1. **`YouTubeService`** (`app/services/youtube_service.py`):
   - Validates URLs and parses video IDs.
   - Extracts metadata (oEmbed & yt-dlp) and native captions via `youtube-transcript-api`.
2. **`AudioService`** (`app/services/audio_service.py`):
   - Downloads audio with `yt-dlp`, normalizes to 16kHz mono WAV via FFmpeg, and manages temporary directories with guaranteed cleanup.
3. **`TranscriptionService` & `stt_providers.py`** (`app/services/`):
   - Abstract `SpeechToTextProvider` with `SarvamSTTProvider` (Indic/Hindi/Hinglish) and `WhisperSTTProvider` (English faster-whisper).
4. **`LLMProvider` & `MistralLLMProvider`** (`app/services/llm_provider.py`):
   - Interacts with Mistral AI using structured educational prompt templates.
5. **`VectorService` & `EmbeddingService`** (`app/services/vector_service.py`):
   - Creates semantic chunks with timestamp anchors, generates dense embeddings, and runs cosine similarity searches scoped to video IDs.
6. **`RAGService`** (`app/services/rag_service.py`):
   - Retrieves top chunks, formats context with time markers, and prompts Mistral for grounded answers and timestamp citations.

---

## 📡 REST & SSE API Endpoint Reference

### 1. `GET /api/v1/health`
Probes the health of the FastAPI server, PostgreSQL database, and Redis broker.

**Response `200 OK`:**
```json
{
  "status": "healthy",
  "app_name": "ExplainMe",
  "version": "1.0.0",
  "timestamp": "2026-10-07T00:00:00.000000Z",
  "services": {
    "database": { "status": "healthy", "type": "PostgreSQL" },
    "redis": { "status": "healthy" }
  }
}
```

---

### 2. `POST /api/v1/videos/analyze`
Submits a YouTube video URL for background analysis.

**Request Body:**
```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "language": "english"
}
```

**Response `202 Accepted`:**
```json
{
  "job_id": "8f9a2b3c-4d5e-6f7a-8b9c-0d1e2f3a4b5c",
  "video_id": "1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d",
  "status": "queued",
  "message": "Video analysis job has been queued successfully."
}
```

**Errors:**
- `400 Bad Request`: Invalid YouTube URL or unparseable Video ID.

---

### 3. `GET /api/v1/jobs/{job_id}`
Retrieves current processing status, stage description, and completion percent.

**Response `200 OK`:**
```json
{
  "id": "8f9a2b3c-4d5e-6f7a-8b9c-0d1e2f3a4b5c",
  "video_id": "1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d",
  "status": "summarizing",
  "progress_percent": 65,
  "current_step": "Generating quick explanation & chapter deep dive...",
  "source_used": "captions",
  "error_message": null,
  "started_at": "2026-10-07T00:00:02Z",
  "completed_at": null,
  "created_at": "2026-10-07T00:00:00Z",
  "updated_at": "2026-10-07T00:00:05Z"
}
```

---

### 4. `GET /api/v1/jobs/{job_id}/events`
Server-Sent Events (SSE) stream emitting real-time job stage changes and percentage updates.

**Event Stream:**
```text
event: job.progress
data: {"job_id": "...", "status": "processing", "progress_percent": 30, "current_step": "Checking for native YouTube captions..."}

event: job.progress
data: {"job_id": "...", "status": "processing", "progress_percent": 65, "current_step": "Generating quick explanation..."}

event: job.completed
data: {"status": "completed"}
```

---

### 5. `GET /api/v1/videos`
Returns paginated list of analyzed videos ordered by most recent creation.

**Parameters:**
- `page`: integer (default: `1`)
- `page_size`: integer (default: `20`)

**Response `200 OK`:**
```json
{
  "items": [
    {
      "id": "1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d",
      "youtube_id": "dQw4w9WgXcQ",
      "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
      "title": "Large Language Models Explained",
      "channel_name": "AI Academy",
      "duration_seconds": 720,
      "thumbnail_url": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
      "view_count": 150000,
      "language_code": "en",
      "created_at": "2026-10-07T00:00:00Z",
      "updated_at": "2026-10-07T00:01:00Z",
      "latest_job_status": "completed",
      "quick_summary_preview": "This video examines foundational principles of neural networks..."
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

---

### 6. `GET /api/v1/videos/{video_id}`
Returns complete video analysis record (quick explanation, detailed summary, key points, keywords, and job status).

**Response `200 OK`:**
```json
{
  "id": "1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d",
  "youtube_id": "dQw4w9WgXcQ",
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "title": "Large Language Models Explained",
  "channel_name": "AI Academy",
  "duration_seconds": 720,
  "thumbnail_url": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
  "view_count": 150000,
  "language_code": "en",
  "created_at": "2026-10-07T00:00:00Z",
  "updated_at": "2026-10-07T00:01:00Z",
  "summary": {
    "id": "...",
    "video_id": "...",
    "quick_summary": "...",
    "detailed_summary": "...",
    "model_used": "mistral-small-latest",
    "language": "en"
  },
  "key_points": [
    {
      "point_index": 1,
      "title": "Self-Attention Mechanism",
      "description": "Explains how tokens compute contextual relevance.",
      "timestamp_seconds": 45.0
    }
  ],
  "keywords": [
    {
      "keyword": "Self-Attention",
      "category": "Concept",
      "relevance_score": 0.95
    }
  ],
  "transcript_preview": "Welcome to this lecture...",
  "transcript_word_count": 1840,
  "latest_job": { ... }
}
```

---

### 7. `GET /api/v1/videos/{video_id}/transcript`
Returns full transcript and timestamped chunk array.

**Response `200 OK`:**
```json
{
  "id": "...",
  "video_id": "...",
  "full_text": "...",
  "language": "en",
  "source_type": "captions",
  "word_count": 1840,
  "chunks": [
    {
      "id": "...",
      "chunk_index": 0,
      "start_time": 0.0,
      "end_time": 15.2,
      "text": "Welcome to this lecture on neural architectures."
    }
  ]
}
```

---

### 8. `GET /api/v1/videos/{video_id}/summary`
Returns quick and detailed summaries for the video.

---

### 9. `POST /api/v1/videos/{video_id}/ask`
Asks a question grounded strictly in the video transcript via RAG vector search.

**Request Body:**
```json
{
  "question": "What is the key advantage of self-attention?"
}
```

**Response `200 OK`:**
```json
{
  "id": "qa-uuid-12345",
  "video_id": "1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d",
  "question": "What is the key advantage of self-attention?",
  "answer": "According to the video, self-attention allows the model to process all tokens in parallel and dynamically weigh the relevance of distant words without sequential bottlenecking.",
  "sources": [
    {
      "chunk_index": 2,
      "start_time": 142.5,
      "end_time": 195.0,
      "text_snippet": "The main advantage of self-attention is parallel computation..."
    }
  ],
  "created_at": "2026-10-07T00:05:00Z"
}
```
