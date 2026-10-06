import logging
from typing import Dict, Any, Optional
from app.core.config import settings
from app.services.audio_service import AudioService
from app.services.stt_providers import (
    SpeechToTextProvider,
    SarvamSTTProvider,
    WhisperSTTProvider,
    STTProviderError,
)

logger = logging.getLogger(__name__)


class TranscriptionService:
    """Service orchestrating audio download and speech-to-text fallback transcription."""

    @classmethod
    def get_provider(cls, language: str = "english") -> SpeechToTextProvider:
        """Select STT provider based on requested language and available API keys."""
        lang_lower = language.lower()
        if ("hinglish" in lang_lower or "hindi" in lang_lower) and settings.SARVAM_API_KEY:
            logger.info("[TranscriptionService] Selecting SarvamSTTProvider for Indic/Hinglish audio.")
            return SarvamSTTProvider(api_key=settings.SARVAM_API_KEY)

        logger.info("[TranscriptionService] Selecting WhisperSTTProvider for audio.")
        return WhisperSTTProvider(model_size=settings.WHISPER_MODEL)

    @classmethod
    def download_audio_and_transcribe(
        cls,
        url: str,
        video_id: str,
        language: str = "english",
    ) -> Optional[Dict[str, Any]]:
        """
        Fallback path: Download audio via yt-dlp to a temporary directory,
        transcribe using the configured STT provider, and clean up temporary files.
        """
        with AudioService.create_temp_directory(prefix=f"explainme_{video_id}_") as temp_dir:
            try:
                audio_path = AudioService.download_youtube_audio(
                    url=url, output_dir=temp_dir, video_id=video_id
                )

                provider = cls.get_provider(language=language)
                result = provider.transcribe(audio_path=audio_path, language=language)

                result["source_type"] = (
                    "sarvam_stt"
                    if isinstance(provider, SarvamSTTProvider)
                    else "whisper_stt"
                )
                result["word_count"] = len(result["full_text"].split())

                return result

            except Exception as exc:
                logger.error(f"[TranscriptionService] Audio fallback transcription failed: {exc}")
                raise
