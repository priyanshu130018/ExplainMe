# UI / UX Design Specification

ExplainMe's frontend is designed as a focused, modern, educational learning studio. It avoids generic chatbot and dashboard clutter in favor of a clean, structured information hierarchy.

---

## 🎨 Visual Identity & Styling System

- **Design Tone:** Intelligent, minimal, educational, readable, dark-canvas modernism.
- **Color Palette:**
  - Background Canvas: `slate-950` (`#090d16`) with subtle ambient indigo gradient glows.
  - Surface Panels: Glassmorphic dark slate `slate-900/90` with fine `slate-800` borders (`rgba(255, 255, 255, 0.08)`).
  - Primary Accent: Indigo/Brand (`#6366f1` / `#4f46e5`).
  - Signal Badges: Emerald (Success/Ready), Amber (Processing/In-Progress), Sky Blue (Topics), Red (Errors).
- **Typography:** Inter (`sans-serif`), clean weights (400, 500, 600, 700, 900) with monospace timestamp markers.

---

## 📱 Page Layouts & Component Breakdown

### 1. Landing Page (`/`)
- **Hero Section:** Clear value proposition: *"Understand any long video in minutes, not hours."*
- **Ingestion Component (`AnalyzeForm`):** Large YouTube URL input with integrated language selector (English, Hindi/Hinglish, Auto-detect) and one-click demo samples.
- **Value Proposition Cards:** Highlights fast-path caption extraction, educational deep dives, grounded Q&A, and precision timestamp jumps.
- **Call-to-Action Banner:** Direct navigation to dashboard.

---

### 2. Studio Dashboard (`/dashboard`)
- **Header & Ingestion Bar:** Quick submission form at the top of the workspace.
- **Stats Overview (`StatsOverview`):** Real-time metric cards (total analyzed videos, average speed, RAG status).
- **Recent Analyses Grid (`RecentVideoCard`):**
  - High-res YouTube thumbnail with duration badge.
  - Live status pill (`Ready`, `Analyzing...`, `Failed`).
  - Channel name, analysis date, title, and quick overview preview.
  - Interactive hover state and direct navigation to analysis detail.

---

### 3. Video Analysis Studio (`/video/:videoId`)
The core workspace for understanding video content.

#### A. Video Hero & Playback (`VideoHero`)
- Embedded YouTube nocookie player with dynamic timestamp seeking (`seekTime` parameter).
- Real-time status indicator, video metadata (channel, duration, view count), and external YouTube link.

#### B. Pipeline Checklist (`ProcessingStages`)
Displayed when a video is being processed:
- Animated progress bar with percentage counter.
- Step-by-step checklist:
  - `✓ Getting video details & metadata`
  - `✓ Retrieving captions & speech transcript`
  - `✓ Normalizing & segmenting transcript`
  - `● Generating quick & detailed explanations`
  - `○ Extracting key takeaways & keywords`
  - `○ Indexing vector knowledge base for Q&A`
  - `○ Finalizing knowledge assets`

#### C. Tabbed Navigation (`Tabs`)
- **Overview Tab:** Quick 3-5 sentence explanation (`QuickExplanation`) + numbered key takeaways (`KeyTakeaways`) with timestamp jump buttons.
- **Detailed Breakdown Tab:** Educational chapter deep dive with concept sections in Markdown (`DetailedBreakdown`).
- **Key Ideas Tab:** Standalone view of core insights with jump-to-time buttons (`▶ MM:SS`).
- **Transcript Tab:** Complete transcript viewer with search filter, word count metrics, and interactive line-by-line timestamp jump buttons (`TranscriptViewer`).
- **Ask ExplainMe Tab:** Grounded conversational tutor chat with clickable citation pills (`AskTutorSection`).

---

### 4. Analysis History (`/history`)
- Searchable and filterable archive of all analyzed videos.
- Instant search filter by video title or channel name.
- Empty states with call-to-action prompts.

---

## 🔄 Interaction Mechanics

1. **Timestamp Jump Interaction:**
   - Clicking any timestamp pill (`▶ 04:15` or `04:15`) in Key Takeaways, Transcript, or Tutor Chat updates the player URL query to `start=255`, smoothly jumps video playback to that exact second, and scrolls to the top of the player.
2. **Real-Time Job Sync:**
   - Frontend listens to Server-Sent Events (`/jobs/{job_id}/events`) with TanStack Query interval polling fallback, ensuring live progress updates without requiring page refreshes.
3. **Clipboard Copying:**
   - One-click copy buttons with transient visual checkmark confirmations across quick summaries and transcript views.
