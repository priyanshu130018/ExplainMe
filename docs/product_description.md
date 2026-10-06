# ExplainMe — Product Description & Vision

> **Help users understand long videos quickly.**

ExplainMe is an AI-powered video understanding platform and interactive video tutor. It transforms complex, lengthy YouTube videos—such as university lectures, technical podcasts, conference talks, and software tutorials—into structured, actionable educational insights.

---

## 🎯 The Problem

- **Time-Consuming Video Content:** A 2-hour technical lecture or podcast contains critical concepts, but finding specific insights requires scrubbing through hours of footage.
- **Generic Summarizers Fall Short:** Traditional text shorteners produce bland, superficial summaries (e.g. *"In this video, the speaker discusses many interesting topics..."*) that fail to teach the material.
- **Unsearchable Knowledge:** Video audio is opaque and disconnected from interactive study workflows.
- **Hallucinating AI:** General chat models frequently hallucinate facts when asked about long multimedia content because they lack strict grounding.

---

## 💡 The Solution: ExplainMe

ExplainMe functions as an intelligent video tutor designed around comprehension and verification:

1. **Fast-Path Understanding:** Users paste a YouTube URL and get high-signal insights in seconds without downloading massive media files whenever native captions exist.
2. **Multi-Level Comprehension:**
   - **Quick Explanation:** 3-5 concise sentences explaining what the video is about, its core thesis, and why it matters.
   - **Detailed Chapter Deep Dive:** Comprehensive lessons broken into structured chapters with key concepts in Markdown.
   - **Key Ideas with Timestamp Anchors:** Actionable takeaways that link directly to video moments (`▶ 04:12`).
   - **Topic & Concept Keywords:** Categorized tags for fast scanning.
3. **Interactive Transcript:** Searchable, readable full transcripts with jump-to-time navigation.
4. **Ask ExplainMe (Grounded Tutor):** An AI chat tutor that answers follow-up questions strictly from the video's spoken words, returning exact timestamp references so learners can verify every claim.

---

## 👥 Target Users & Primary Use Cases

- **Students & Researchers:** Digest 90-minute lectures, extract exam-ready takeaways, and ask targeted questions about complex formulas or theorems.
- **Software Engineers & Developers:** Extract architectural decisions, syntax walkthroughs, and key takeaways from 2-hour conference talks and coding tutorials.
- **Professionals & Knowledge Workers:** Review recorded webinars, industry keynotes, and expert panels in minutes.
- **Curious Learners:** Grasp the core insights of podcasts and documentaries without committing hours to passive watching.

---

## 🌟 Current Scope vs. Future Roadmap

### Current Capabilities
- Full YouTube ingestion with fast captions and STT audio fallback (Sarvam AI & Whisper).
- LangGraph orchestration with Mistral AI.
- Neon PostgreSQL persistence with pgvector semantic search.
- Interactive React studio with embedded playback, timestamp seeking, and grounded Q&A.
- Docker Compose local development environment.

### Future Roadmap
- **Browser Extension:** Chrome extension for in-page YouTube side-panel analysis.
- **Multi-Video Playlists & Channels:** Cross-video synthesis and collective knowledge querying.
- **Export & Notes Integration:** Direct export to Notion, Obsidian, and PDF study guides.
- **User Accounts & Cloud Bookmarks:** Multi-user workspaces and team study folders.
