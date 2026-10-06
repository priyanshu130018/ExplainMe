import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


class STTProviderError(Exception):
    """Raised when speech-to-text transcription fails."""


class SpeechToTextProvider(ABC):
    """Abstract base class for all Speech-to-Text providers."""

    @abstractmethod
    def transcribe(self, audio_path: str, language: str = "english") -> Dict[str, Any]:
        """
        Transcribe an audio file.
        Returns a dict with:
          - full_text: str
          - chunks: List[dict] with {chunk_index, start_time, end_time, text}
          - language: str
        """
        pass


class SarvamSTTProvider(SpeechToTextProvider):
    """Sarvam AI speech-to-text provider for Indic, Hindi, and Hinglish audio."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.SARVAM_API_KEY

    def transcribe(self, audio_path: str, language: str = "hinglish") -> Dict[str, Any]:
        if not self.api_key:
            raise STTProviderError("SARVAM_API_KEY is not configured in environment.")

        url = "https://api.sarvam.ai/speech-to-text-translate"
        headers = {
            "api-subscription-key": self.api_key,
        }

        try:
            with open(audio_path, "rb") as f:
                files = {"file": (os.path.basename(audio_path), f, "audio/wav")}
                data = {"model": "saaras:v1"}
                response = httpx.post(url, headers=headers, files=files, data=data, timeout=60.0)

            if response.status_code != 200:
                raise STTProviderError(f"Sarvam AI STT API error {response.status_code}: {response.text}")

            result = response.json()
            transcript_text = result.get("transcript", "").strip()

            return {
                "full_text": transcript_text,
                "chunks": [
                    {
                        "chunk_index": 0,
                        "start_time": 0.0,
                        "end_time": 0.0,
                        "text": transcript_text,
                    }
                ],
                "language": "hi-Latn" if language == "hinglish" else "hi",
            }
        except Exception as exc:
            logger.error(f"[SarvamSTTProvider] Transcription failed: {exc}")
            raise STTProviderError(f"Sarvam AI transcription failed: {str(exc)}") from exc


class WhisperSTTProvider(SpeechToTextProvider):
    """Local faster-whisper / OpenAI Whisper speech-to-text provider."""

    def __init__(self, model_size: Optional[str] = None):
        self.model_size = model_size or settings.WHISPER_MODEL

    def transcribe(self, audio_path: str, language: str = "english") -> Dict[str, Any]:
        logger.info(f"[WhisperSTTProvider] Loading Whisper model ({self.model_size})...")

        # Try faster-whisper first for high performance
        try:
            from faster_whisper import WhisperModel
            model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
            segments, info = model.transcribe(
                audio_path,
                beam_size=5,
                language="en" if language == "english" else None,
            )

            chunks = []
            full_text_parts = []
            for idx, segment in enumerate(segments):
                text = segment.text.strip()
                if not text:
                    continue
                chunks.append({
                    "chunk_index": idx,
                    "start_time": round(segment.start, 2),
                    "end_time": round(segment.end, 2),
                    "text": text,
                })
                full_text_parts.append(text)

            return {
                "full_text": " ".join(full_text_parts).strip(),
                "chunks": chunks,
                "language": info.language or "en",
            }
        except ImportError:
            pass

        # Fallback to standard openai-whisper
        try:
            import whisper
            model = whisper.load_model(self.model_size)
            result = model.transcribe(audio_path, language="en" if language == "english" else None)

            chunks = []
            segments = result.get("segments", [])
            for idx, seg in enumerate(segments):
                text = seg.get("text", "").strip()
                if not text:
                    continue
                chunks.append({
                    "chunk_index": idx,
                    "start_time": round(seg.get("start", 0.0), 2),
                    "end_time": round(seg.get("end", 0.0), 2),
                    "text": text,
                })

            return {
                "full_text": result.get("text", "").strip(),
                "chunks": chunks,
                "language": result.get("language", "en"),
            }
        except ImportError:
            raise STTProviderError(
                "Neither faster-whisper nor whisper is installed in the current environment."
            )
        except Exception as exc:
            logger.error(f"[WhisperSTTProvider] Whisper transcription failed: {exc}")
            raise STTProviderError(f"Whisper transcription failed: {str(exc)}") from exc
