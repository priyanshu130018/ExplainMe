import re
import urllib.parse
from typing import Optional, Dict, Any, List
import httpx

try:
    from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
    HAS_YT_TRANSCRIPT = True
except ImportError:
    HAS_YT_TRANSCRIPT = False
    YouTubeTranscriptApi = None
    TranscriptsDisabled = Exception
    NoTranscriptFound = Exception


class YouTubeService:
    """Service for validating, parsing, fetching metadata and captions from YouTube videos."""

    YOUTUBE_REGEX = re.compile(
        r"^(https?://)?(www\.|m\.)?(youtube\.com/(?:watch\?v=|embed/|v/|shorts/)|youtu\.be/)([\w-]{11})"
    )

    @classmethod
    def is_valid_url(cls, url: str) -> bool:
        if not url:
            return False
        return bool(cls.YOUTUBE_REGEX.search(url.strip()))

    @classmethod
    def extract_video_id(cls, url: str) -> Optional[str]:
        if not url:
            return None
        url = url.strip()
        match = cls.YOUTUBE_REGEX.search(url)
        if match:
            return match.group(4)
        
        # Fallback query param parsing
        parsed = urllib.parse.urlparse(url)
        if parsed.hostname in ("youtube.com", "www.youtube.com", "m.youtube.com"):
            qs = urllib.parse.parse_qs(parsed.query)
            if "v" in qs and qs["v"]:
                return qs["v"][0]
        elif parsed.hostname == "youtu.be":
            return parsed.path.lstrip("/")
        return None

    @classmethod
    def fetch_metadata(cls, url: str, video_id: str) -> Dict[str, Any]:
        """
        Fetch video metadata including title, author, thumbnail, and duration.
        Uses YouTube oEmbed endpoint first for speed, falling back to yt-dlp if needed.
        """
        metadata = {
            "youtube_id": video_id,
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "title": f"YouTube Video ({video_id})",
            "channel_name": None,
            "thumbnail_url": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
            "duration_seconds": None,
            "view_count": None,
        }

        try:
            oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
            with httpx.Client(timeout=5.0) as client:
                res = client.get(oembed_url)
                if res.status_code == 200:
                    data = res.json()
                    metadata["title"] = data.get("title", metadata["title"])
                    metadata["channel_name"] = data.get("author_name")
                    if data.get("thumbnail_url"):
                        metadata["thumbnail_url"] = data.get("thumbnail_url")
        except Exception:
            pass

        # If title still default, try yt-dlp metadata extract without download
        if metadata["title"].startswith("YouTube Video"):
            try:
                import yt_dlp
                ydl_opts = {
                    "skip_download": True,
                    "quiet": True,
                    "no_warnings": True,
                    "extract_flat": True,
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    if info:
                        metadata["title"] = info.get("title", metadata["title"])
                        metadata["channel_name"] = info.get("uploader") or metadata["channel_name"]
                        metadata["duration_seconds"] = info.get("duration")
                        metadata["view_count"] = info.get("view_count")
            except Exception:
                pass

        return metadata

    @classmethod
    def get_captions_transcript(cls, video_id: str, preferred_languages: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """
        Fast Path: Retrieve native transcript captions using youtube-transcript-api.
        Returns dict with 'full_text', 'chunks' (timestamped), and 'language'.
        """
        if not HAS_YT_TRANSCRIPT or not YouTubeTranscriptApi:
            return None

        if not preferred_languages:
            preferred_languages = ["en", "en-US", "en-GB", "hi", "hi-Latn"]

        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Find matching transcript
            transcript_obj = None
            try:
                transcript_obj = transcript_list.find_transcript(preferred_languages)
            except Exception:
                try:
                    transcript_obj = transcript_list.find_generated_transcript(preferred_languages)
                except Exception:
                    for t in transcript_list:
                        transcript_obj = t
                        break

            if not transcript_obj:
                return None

            raw_entries = transcript_obj.fetch()
            chunks = []
            full_text_parts = []

            for idx, entry in enumerate(raw_entries):
                text = entry.get("text", "").replace("\n", " ").strip()
                if not text:
                    continue
                start = entry.get("start", 0.0)
                duration = entry.get("duration", 0.0)
                chunks.append({
                    "chunk_index": idx,
                    "start_time": round(start, 2),
                    "end_time": round(start + duration, 2),
                    "text": text,
                })
                full_text_parts.append(text)

            full_text = " ".join(full_text_parts).strip()
            if not full_text:
                return None

            return {
                "full_text": full_text,
                "chunks": chunks,
                "language": transcript_obj.language_code,
                "source_type": "captions",
                "word_count": len(full_text.split()),
            }

        except (TranscriptsDisabled, NoTranscriptFound):
            return None
        except Exception as e:
            print(f"[YouTubeService] Transcript fetch error: {e}")
            return None
