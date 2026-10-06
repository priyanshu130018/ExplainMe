# ExplainMe — AI-Powered Video Understanding & Tutor

> **Transform long videos into clear, structured insights and interactive conversational tutoring.**

ExplainMe is an AI-powered video comprehension platform that converts long YouTube lectures, technical podcasts, keynote presentations, and tutorials into concise quick summaries, detailed chapter deep dives, actionable key takeaways, topic keywords, full searchable transcripts, and grounded conversational Q&A with precision timestamp citations.

---

## 📑 Table of Contents

1. [Overview](#1-overview)
2. [Features](#2-features)
3. [How It Works](#3-how-it-works)
4. [Architecture](#4-architecture)
5. [Technology Stack](#5-technology-stack)
6. [Project Structure](#6-project-structure)
7. [Prerequisites](#7-prerequisites)
8. [Environment Variables](#8-environment-variables)
9. [Neon Database Setup](#9-neon-database-setup)
10. [Database Migrations](#10-database-migrations)
11. [Running with Docker](#11-running-with-docker)
12. [Running Backend Locally](#12-running-backend-locally)
13. [Running Frontend Locally](#13-running-frontend-locally)
14. [Running Celery Worker](#14-running-celery-worker)
15. [API Documentation](#15-api-documentation)
16. [API Endpoint Reference](#16-api-endpoint-reference)
17. [Testing](#17-testing)
18. [Development Workflow](#18-development-workflow)
19. [Troubleshooting](#19-troubleshooting)
20. [Documentation](#20-documentation)
21. [Future Roadmap](#21-future-roadmap)
22. [License](#22-license)

---

## 1. Overview

ExplainMe is designed to help learners and professionals understand video content efficiently. Rather than simply shortening video transcripts, ExplainMe structures the knowledge hierarchically and provides an interactive AI tutor grounded strictly in the spoken video content to eliminate hallucinations.

---

## 2. Features

- ⚡ **Captions Fast-Path:** Instant caption extraction via `youtube-transcript-api` without downloading multi-gigabyte video or audio files.
- 🎙️ **Audio STT Fallback:** Graceful fallback to `yt-dlp` + FFmpeg audio extraction and speech-to-text via Sarvam AI (Indic/Hindi/Hinglish) or Whisper (English).
- 💡 **Multi-Level Summarization:**
  - **Quick Explanation:** 3–5 high-signal sentences explaining the core premise, key mechanism, and practical significance.
  - **Detailed Chapter Breakdown:** Structured educational lessons in Markdown with chapter headings and concept explanations.
- 📌 **Actionable Key Takeaways:** 5–8 specific insights anchored to video timestamps (`▶ 04:12`).
- 🏷️ **Categorized Topic Keywords:** Categorized topic tags (`Concept`, `Tool`, `Method`, `Domain`).
- 📜 **Searchable Interactive Transcript:** Full transcript viewer with real-time text search and timestamp jump buttons.
- 🤖 **Ask ExplainMe (Grounded Tutor):** Interactive conversational chat grounded in video transcripts using pgvector similarity search, complete with clickable timestamp sources.
- 🔄 **Real-Time Pipeline Progress:** Server-Sent Events (SSE) and polling updates showing live stage progression.

---

## 3. How It Works

```text
User pastes YouTube URL
         ↓
FastAPI receives request & validates URL
         ↓
Celery queues background task (Redis)
         ↓
LangGraph Pipeline executes:
   1. Fetch Video Metadata
   2. Retrieve Captions (or Audio Fallback STT)
   3. Segment into Semantic Chunks with Timestamps
   4. Generate Quick & Detailed Explanations (Mistral)
   5. Extract Key Points & Keywords
   6. Generate 384-dim Vector Embeddings
   7. Persist to Neon PostgreSQL (pgvector)
         ↓
React Studio updates in real time with interactive insights & Q&A
```

---

## 4. Architecture

```text
┌─────────────────────────┐
│     React 18 + Vite     │ (Tailwind CSS, TanStack Query, React Router)
└────────────┬────────────┘
             │ HTTP / SSE
             ▼
┌─────────────────────────┐
│       FastAPI API       │ (Pydantic v2, Dependency Injection)
└──────┬───────────┬──────┘
       │           │
       ▼           ▼
┌──────────────┐ ┌──────────────┐
│ Neon Postgre │ │ Redis Broker │
│  + pgvector  │ └──────┬───────┘
└──────────────┘        │
                        ▼
                 ┌──────────────┐
                 │Celery Worker │ (LangGraph + Mistral + Whisper/Sarvam)
                 └──────────────┘
```

---

## 5. Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 18, TypeScript, Vite, React Router v6, Tailwind CSS, TanStack Query v5, Lucide Icons |
| **Backend API** | Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy 2, Alembic |
| **Database** | Neon Serverless PostgreSQL + pgvector extension |
| **Task Queue & Cache**| Celery + Redis |
| **AI Orchestration** | LangGraph, LangChain, Mistral AI (`mistral-small-latest`) |
| **Speech Processing** | `youtube-transcript-api`, `yt-dlp`, FFmpeg, Sarvam AI, faster-whisper |
| **Embeddings** | SentenceTransformers (`all-MiniLM-L6-v2`, 384 dimensions) |
| **Containerization** | Docker, Docker Compose, Nginx |

---

## 6. Project Structure

```text
ExplainMe/
├── docs/                        # Comprehensive Architecture & Design Docs
│   ├── db_schema.md             # Database & pgvector specifications
│   ├── api_backend_design.md    # FastAPI endpoints and service layer design
│   ├── ui_ux_design.md          # UI design system and page flows
│   ├── ai_workflow_design.md    # LangGraph pipeline and RAG architecture
│   └── product_description.md   # Product vision and user journeys
│
├── frontend/                    # React 18 + Vite + TypeScript Application
│   ├── src/
│   │   ├── api/                 # Strongly typed API client methods
│   │   ├── components/          # Reusable UI, Dashboard, and Video components
│   │   ├── hooks/               # TanStack Query & SSE hooks
│   │   ├── lib/                 # Utility helpers & constants
│   │   ├── pages/               # LandingPage, DashboardPage, VideoDetailPage, HistoryPage
│   │   ├── routes/              # React Router configuration
│   │   └── types/               # TypeScript interfaces
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
│
├── backend/                     # FastAPI + SQLAlchemy + Celery Application
│   ├── app/
│   │   ├── api/                 # FastAPI routes (health, videos, jobs)
│   │   ├── core/                # Configuration (Pydantic BaseSettings) & Celery app
│   │   ├── db/                  # SQLAlchemy 2 Base, Session, and Engine
│   │   ├── models/              # Relational models (Video, Job, Transcript, etc.)
│   │   ├── schemas/             # Pydantic v2 schemas
│   │   ├── services/            # YouTube, Audio, STT, LLM, Vector, and RAG services
│   │   ├── workflows/           # LangGraph video analysis pipeline
│   │   └── workers/             # Celery background tasks
│   ├── alembic/                 # Database migrations
│   ├── tests/                   # Pytest test suite
│   ├── requirements.txt
│   └── Dockerfile
│
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## 7. Prerequisites

- [Docker & Docker Compose](https://docs.docker.com/get-docker/) (Recommended) OR
- Node.js 18+ and Python 3.10+ with system FFmpeg installed.

---

## 8. Environment Variables

Create `.env` in the root directory:

```bash
cp .env.example .env
```

| Variable | Required | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | **Yes** | Neon PostgreSQL connection string (`postgresql://USER:PASSWORD@HOST/DATABASE?sslmode=require`) |
| `REDIS_URL` | **Yes** | Redis connection URL (`redis://localhost:6379/0` or `redis://redis:6379/0`) |
| `CELERY_BROKER_URL` | **Yes** | Celery broker URL (same as `REDIS_URL`) |
| `CELERY_RESULT_BACKEND` | **Yes** | Celery result backend URL |
| `MISTRAL_API_KEY` | **Yes** | Mistral AI API Key ([console.mistral.ai](https://console.mistral.ai)) |
| `MISTRAL_MODEL` | No | Mistral model identifier (default: `mistral-small-latest`) |
| `SARVAM_API_KEY` | Optional | Sarvam AI key for Hindi/Hinglish speech translation |
| `WHISPER_MODEL` | No | Model size for local Whisper fallback (default: `base`) |
| `AUTH_SECRET` | No | Secret key for token signing |
| `VITE_API_BASE_URL` | No | Frontend API base URL (default: `/api/v1`) |

---

## 9. Neon Database Setup

1. Create a serverless PostgreSQL database at [Neon](https://neon.tech).
2. Copy the Connection String from the Neon dashboard.
3. Paste it as `DATABASE_URL` in `.env`:
   ```env
   DATABASE_URL=postgresql://USER:PASSWORD@HOST.neon.tech/neondb?sslmode=require
   ```
4. ExplainMe automatically enables the `pgvector` extension and creates all required tables.

---

## 10. Database Migrations

Apply Alembic migrations to Neon PostgreSQL:

```bash
cd backend
alembic upgrade head
```

To create a new migration after editing models:
```bash
alembic revision --autogenerate -m "describe_changes"
```

---

## 11. Running with Docker

Start all 4 services (`frontend`, `backend`, `worker`, `redis`) with a single command:

```bash
docker compose up --build -d
```

### Access URLs
- **Web Application:** [http://localhost](http://localhost) (or [http://localhost:5173](http://localhost:5173))
- **FastAPI Documentation (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check:** [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

To view logs:
```bash
docker compose logs -f backend
docker compose logs -f worker
```

To stop all containers:
```bash
docker compose down
```

---

## 12. Running Backend Locally

```bash
cd backend
python -m venv .venv

# Windows:
.\.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

---

## 13. Running Frontend Locally

```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173).

---

## 14. Running Celery Worker

In a separate terminal (with Redis running):

```bash
cd backend
celery -A app.core.celery_app.celery_app worker --loglevel=info
```

---

## 15. API Documentation

Interactive Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)  
ReDoc API Specification: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 16. API Endpoint Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Service health probes (API, PostgreSQL, Redis) |
| `POST` | `/api/v1/videos/analyze` | Submit a YouTube URL for background analysis (returns `job_id`) |
| `GET` | `/api/v1/jobs/{job_id}` | Poll analysis progress and current step |
| `GET` | `/api/v1/jobs/{job_id}/events`| Server-Sent Events stream for live job stage updates |
| `GET` | `/api/v1/videos` | List analyzed videos (paginated) |
| `GET` | `/api/v1/videos/{video_id}` | Complete video details, summaries, key takeaways, and keywords |
| `GET` | `/api/v1/videos/{video_id}/transcript` | Full transcript with timestamped chunks |
| `GET` | `/api/v1/videos/{video_id}/summary` | Quick and detailed summaries |
| `POST` | `/api/v1/videos/{video_id}/ask` | Ask a grounded question with timestamp citations |

---

## 17. Testing

### Run Backend Test Suite:
```bash
cd backend
python -m pytest tests -v
```

### Run Frontend Production Build & Type Check:
```bash
cd frontend
npm run build
```

---

## 18. Development Workflow

1. Update database models in `backend/app/models/`.
2. Generate migration: `alembic revision --autogenerate -m "update_models"`.
3. Apply migration: `alembic upgrade head`.
4. Run tests: `pytest tests -v` and `npm run build`.
5. Test locally or in Docker: `docker compose up --build`.

---

## 19. Troubleshooting

- **Redis Connection Failed:** Ensure Redis is running locally (`redis-server`) or use Docker Compose.
- **Neon SSL Warning:** Ensure `sslmode=require` is appended to `DATABASE_URL`.
- **Audio Fallback Issues:** Ensure `ffmpeg` is installed in your system PATH (`ffmpeg -version`).

---

## 20. Documentation

Comprehensive architecture specifications are available in the `docs/` folder:
- [`docs/db_schema.md`](docs/db_schema.md): Database & pgvector specifications.
- [`docs/api_backend_design.md`](docs/api_backend_design.md): FastAPI architecture and API reference.
- [`docs/ui_ux_design.md`](docs/ui_ux_design.md): Frontend design system and UI components.
- [`docs/ai_workflow_design.md`](docs/ai_workflow_design.md): LangGraph pipeline and RAG grounding workflow.
- [`docs/product_description.md`](docs/product_description.md): Product vision, value proposition, and user journeys.

---

## 21. Future Roadmap

- 🧩 **Chrome Extension:** In-page YouTube side-panel companion.
- 📚 **Playlist Analysis:** Multi-video synthesis and collective knowledge querying.
- 📝 **Export Integrations:** Export study notes to Notion, Obsidian, and PDF.

---

## 22. License

MIT License &copy; 2026 ExplainMe.
