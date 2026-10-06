# Database Architecture & Schema Specification

ExplainMe utilizes **Neon PostgreSQL** (serverless PostgreSQL with branching and connection pooling) combined with the **pgvector** extension for high-performance vector similarity search across video transcript chunks.

---

## 🏛️ Architecture Overview

The database is designed with third-normal-form relational integrity and vector extensions to support:
- Persistent video metadata and playback references.
- Asynchronous Celery analysis jobs with stage tracking.
- Hierarchical transcript storage (full text + timestamped semantic chunks).
- Dense 384-dimensional vector embeddings stored natively in PostgreSQL.
- Structured AI summaries, key takeaways, and categorized keywords.
- Transcript-grounded Question & Answer history with source references.

```text
 ┌────────────────┐         1:N         ┌──────────────────┐
 │     videos     ├────────────────────►│  analysis_jobs   │
 └───┬───┬───┬────┘                     └──────────────────┘
     │   │   │
     │   │   │ 1:1                      ┌──────────────────┐
     │   │   └─────────────────────────►│    summaries     │
     │   │                              └──────────────────┘
     │   │ 1:1
     │   ├─────────────────────────────►┌──────────────────┐
     │   │                              │   transcripts    │
     │   │                              └──────────────────┘
     │   │ 1:N
     │   ├─────────────────────────────►┌──────────────────┐
     │   │                              │transcript_chunks │ (Vector 384)
     │   │                              └──────────────────┘
     │   │ 1:N
     │   ├─────────────────────────────►┌──────────────────┐
     │   │                              │    key_points    │
     │   │                              └──────────────────┘
     │   │ 1:N
     │   ├─────────────────────────────►┌──────────────────┐
     │   │                              │     keywords     │
     │   │                              └──────────────────┘
     │   │ 1:N
     │   └─────────────────────────────►┌──────────────────┐
     │                                  │ question_answers │
     ▼                                  └──────────────────┘
┌────────┐
│ users  │ (Future Auth Support)
└────────┘
```

---

## 📊 Database Models & Tables

### 1. `videos`
Stores core video metadata obtained from YouTube.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `VARCHAR(36)` | `PRIMARY KEY` | UUID v4 identifier |
| `youtube_id` | `VARCHAR(32)` | `UNIQUE, INDEX, NOT NULL` | YouTube 11-character video ID |
| `url` | `VARCHAR(512)` | `NOT NULL` | Normalized YouTube watch URL |
| `title` | `VARCHAR(512)` | `NOT NULL` | Human-readable video title |
| `channel_name` | `VARCHAR(255)` | `NULLABLE` | Author / Uploader channel name |
| `duration_seconds` | `INTEGER` | `NULLABLE` | Total duration in seconds |
| `thumbnail_url` | `VARCHAR(512)` | `NULLABLE` | Maxres / High-res thumbnail URL |
| `view_count` | `INTEGER` | `NULLABLE` | Total views when fetched |
| `language_code` | `VARCHAR(16)` | `NOT NULL, DEFAULT 'en'` | Spoken language ISO code |
| `created_at` | `TIMESTAMP` | `NOT NULL` | UTC creation timestamp |
| `updated_at` | `TIMESTAMP` | `NOT NULL` | UTC last modified timestamp |

---

### 2. `analysis_jobs`
Tracks asynchronous Celery background tasks, progress percentage, and pipeline status.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `VARCHAR(36)` | `PRIMARY KEY` | UUID v4 identifier |
| `video_id` | `VARCHAR(36)` | `FOREIGN KEY (videos.id) ON DELETE CASCADE, INDEX` | Linked video |
| `user_id` | `VARCHAR(36)` | `FOREIGN KEY (users.id) ON DELETE SET NULL, NULLABLE` | Optional user owner |
| `status` | `VARCHAR(32)` | `INDEX, NOT NULL` | `queued`, `downloading`, `transcribing`, `summarizing`, `indexing`, `completed`, `failed` |
| `progress_percent` | `INTEGER` | `NOT NULL, DEFAULT 0` | Current progress integer (0–100) |
| `current_step` | `VARCHAR(128)` | `NOT NULL` | Step description shown to user |
| `source_used` | `VARCHAR(32)` | `NULLABLE` | `captions`, `whisper_stt`, `sarvam_stt` |
| `error_message` | `TEXT` | `NULLABLE` | User-safe error description if failed |
| `celery_task_id` | `VARCHAR(64)` | `NULLABLE` | Celery asynchronous task UUID |
| `started_at` | `TIMESTAMP` | `NULLABLE` | Processing start time |
| `completed_at` | `TIMESTAMP` | `NULLABLE` | Completion timestamp |
| `created_at` | `TIMESTAMP` | `NOT NULL` | UTC creation timestamp |
| `updated_at` | `TIMESTAMP` | `NOT NULL` | UTC last modified timestamp |

---

### 3. `transcripts`
Stores full concatenated transcript text and extraction metrics.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `VARCHAR(36)` | `PRIMARY KEY` | UUID v4 identifier |
| `video_id` | `VARCHAR(36)` | `FOREIGN KEY (videos.id) ON DELETE CASCADE, UNIQUE, INDEX` | 1:1 relationship with `videos` |
| `full_text` | `TEXT` | `NOT NULL` | Complete transcribed text |
| `language` | `VARCHAR(16)` | `NOT NULL, DEFAULT 'en'` | Detected or requested transcript language |
| `source_type` | `VARCHAR(32)` | `NOT NULL` | `captions` or `audio_stt` |
| `word_count` | `INTEGER` | `NOT NULL, DEFAULT 0` | Total word count |
| `created_at` | `TIMESTAMP` | `NOT NULL` | UTC timestamp |
| `updated_at` | `TIMESTAMP` | `NOT NULL` | UTC timestamp |

---

### 4. `transcript_chunks`
Timestamp-preserved transcript segments with **pgvector** dense embeddings.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `VARCHAR(36)` | `PRIMARY KEY` | UUID v4 identifier |
| `video_id` | `VARCHAR(36)` | `FOREIGN KEY (videos.id) ON DELETE CASCADE, INDEX` | Scoped to parent video |
| `chunk_index` | `INTEGER` | `INDEX, NOT NULL` | Sequential segment order |
| `start_time` | `FLOAT` | `NOT NULL` | Start timestamp in seconds |
| `end_time` | `FLOAT` | `NOT NULL` | End timestamp in seconds |
| `text` | `TEXT` | `NOT NULL` | Spoken text within this time window |
| `embedding` | `VECTOR(384)` | `NULLABLE` | 384-dimensional cosine similarity vector |
| `created_at` | `TIMESTAMP` | `NOT NULL` | UTC timestamp |
| `updated_at` | `TIMESTAMP` | `NOT NULL` | UTC timestamp |

---

### 5. `summaries`
AI-generated high-level quick overview and chapter deep dive.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `VARCHAR(36)` | `PRIMARY KEY` | UUID v4 identifier |
| `video_id` | `VARCHAR(36)` | `FOREIGN KEY (videos.id) ON DELETE CASCADE, UNIQUE, INDEX` | 1:1 relationship with `videos` |
| `quick_summary` | `TEXT` | `NOT NULL` | 3-5 sentence educational overview |
| `detailed_summary` | `TEXT` | `NOT NULL` | Structured chapter breakdowns in Markdown |
| `model_used` | `VARCHAR(64)` | `NOT NULL` | LLM identifier (e.g. `mistral-small-latest`) |
| `language` | `VARCHAR(16)` | `NOT NULL` | Language code |
| `created_at` | `TIMESTAMP` | `NOT NULL` | UTC timestamp |
| `updated_at` | `TIMESTAMP` | `NOT NULL` | UTC timestamp |

---

### 6. `key_points`
Specific, actionable insights extracted from the video with timestamp references.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `VARCHAR(36)` | `PRIMARY KEY` | UUID v4 identifier |
| `video_id` | `VARCHAR(36)` | `FOREIGN KEY (videos.id) ON DELETE CASCADE, INDEX` | Linked video |
| `point_index` | `INTEGER` | `NOT NULL` | Sequence order (1–8) |
| `title` | `VARCHAR(255)` | `NOT NULL` | Point headline |
| `description` | `TEXT` | `NOT NULL` | Detailed takeaway explanation |
| `timestamp_seconds` | `FLOAT` | `NULLABLE` | Video timestamp jump position |
| `created_at` | `TIMESTAMP` | `NOT NULL` | UTC timestamp |
| `updated_at` | `TIMESTAMP` | `NOT NULL` | UTC timestamp |

---

### 7. `keywords`
Categorized concepts, tools, and domain topics extracted from the content.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `VARCHAR(36)` | `PRIMARY KEY` | UUID v4 identifier |
| `video_id` | `VARCHAR(36)` | `FOREIGN KEY (videos.id) ON DELETE CASCADE, INDEX` | Linked video |
| `keyword` | `VARCHAR(128)` | `INDEX, NOT NULL` | Keyword string |
| `category` | `VARCHAR(64)` | `NULLABLE` | `Concept`, `Tool`, `Method`, `Domain` |
| `relevance_score` | `FLOAT` | `NULLABLE` | Score from 0.0 to 1.0 |
| `created_at` | `TIMESTAMP` | `NOT NULL` | UTC timestamp |
| `updated_at` | `TIMESTAMP` | `NOT NULL` | UTC timestamp |

---

### 8. `question_answers`
Persisted interactive Q&A history with citations.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `VARCHAR(36)` | `PRIMARY KEY` | UUID v4 identifier |
| `video_id` | `VARCHAR(36)` | `FOREIGN KEY (videos.id) ON DELETE CASCADE, INDEX` | Scoped video |
| `user_id` | `VARCHAR(36)` | `FOREIGN KEY (users.id) ON DELETE SET NULL, NULLABLE` | Asking user |
| `question` | `TEXT` | `NOT NULL` | User's question |
| `answer` | `TEXT` | `NOT NULL` | Grounded AI answer |
| `sources` | `JSON` | `NULLABLE` | Array of source chunks and timestamp spans |
| `created_at` | `TIMESTAMP` | `NOT NULL` | UTC timestamp |
| `updated_at` | `TIMESTAMP` | `NOT NULL` | UTC timestamp |

---

### 9. `users`
Foundation for future user accounts and authentication.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `VARCHAR(36)` | `PRIMARY KEY` | UUID v4 identifier |
| `email` | `VARCHAR(255)` | `UNIQUE, INDEX, NOT NULL` | User email address |
| `hashed_password` | `VARCHAR(255)` | `NULLABLE` | Password hash |
| `full_name` | `VARCHAR(255)` | `NULLABLE` | Display name |
| `is_active` | `BOOLEAN` | `NOT NULL, DEFAULT TRUE` | Active state |
| `is_superuser` | `BOOLEAN` | `NOT NULL, DEFAULT FALSE` | Admin privileges |
| `created_at` | `TIMESTAMP` | `NOT NULL` | UTC timestamp |
| `updated_at` | `TIMESTAMP` | `NOT NULL` | UTC timestamp |

---

## ⚡ Vector Search & Similarity Mechanics

1. When video processing runs, transcript chunks are embedded using **SentenceTransformers** (`all-MiniLM-L6-v2`, 384 dimensions).
2. Embeddings are stored in `transcript_chunks.embedding` column.
3. During `POST /api/v1/videos/{video_id}/ask`:
   - The question is converted to a 384-dimensional query vector.
   - Vector similarity search retrieves the top-4 chunks strictly matching `video_id`:
     $$\text{Cosine Similarity} = \frac{\mathbf{q} \cdot \mathbf{v}}{\|\mathbf{q}\| \|\mathbf{v}\|}$$
   - Chunks are assembled with timestamps and sent to Mistral for grounded generation.

---

## 🔄 Alembic Migrations
- Migration files are located in `backend/alembic/versions/`.
- Run migrations:
  ```bash
  cd backend
  alembic upgrade head
  ```
