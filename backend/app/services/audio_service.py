import os
import shutil
import tempfile
import subprocess
import logging
from typing import Generator, List, Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class AudioProcessingError(Exception):
    """Raised when audio download, conversion, or chunking fails."""


class AudioService:
    """Service for handling audio extraction, conversion, chunking, and cleanup."""

    @classmethod
    @contextmanager
    def create_temp_directory(cls, prefix: str = "explainme_audio_") -> Generator[str, None, None]:
        """Context manager creating a temporary working directory and ensuring complete cleanup."""
        temp_dir = tempfile.mkdtemp(prefix=prefix)
        try:
            yield temp_dir
        finally:
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
                logger.debug(f"[AudioService] Cleaned up temporary directory: {temp_dir}")
            except Exception as e:
                logger.warning(f"[AudioService] Error cleaning temporary directory {temp_dir}: {e}")

    @classmethod
    def download_youtube_audio(cls, url: str, output_dir: str, video_id: str) -> str:
        """
        Download YouTube video audio track as a 16kHz mono WAV file using yt-dlp.
        Returns the absolute path to the downloaded WAV audio file.
        """
        output_template = os.path.join(output_dir, f"{video_id}.%(ext)s")
        expected_wav_path = os.path.join(output_dir, f"{video_id}.wav")

        try:
            import yt_dlp
        except ImportError:
            raise AudioProcessingError("yt-dlp package is not installed.")

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": output_template,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "wav",
                    "preferredquality": "192",
                }
            ],
            "postprocessor_args": [
                "-ar", "16000",  # 16kHz sample rate optimal for Whisper/STT
                "-ac", "1",      # Mono channel
            ],
            "quiet": True,
            "no_warnings": True,
        }

        try:
            logger.info(f"[AudioService] Downloading audio for YouTube video: {video_id}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            if os.path.exists(expected_wav_path):
                return expected_wav_path

            # Fallback search for any converted audio file in output_dir
            for fname in os.listdir(output_dir):
                if fname.startswith(video_id) and fname.endswith((".wav", ".mp3", ".m4a", ".webm")):
                    return os.path.join(output_dir, fname)

            raise AudioProcessingError(f"Audio file was not created for video {video_id}")

        except Exception as exc:
            logger.error(f"[AudioService] Audio download failed for {url}: {exc}")
            raise AudioProcessingError(f"Failed to download audio from YouTube: {str(exc)}") from exc

    @classmethod
    def chunk_audio_file(
        cls, audio_path: str, chunk_length_seconds: int = 300, output_dir: Optional[str] = None
    ) -> List[str]:
        """
        Split a long audio file into smaller chunks (default 5-minute chunks) for STT APIs.
        Returns a list of paths to audio chunk files.
        """
        if not os.path.exists(audio_path):
            raise AudioProcessingError(f"Audio file not found: {audio_path}")

        work_dir = output_dir or os.path.dirname(audio_path)
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        chunk_pattern = os.path.join(work_dir, f"{base_name}_chunk_%03d.wav")

        cmd = [
            "ffmpeg",
            "-y",
            "-i", audio_path,
            "-f", "segment",
            "-segment_time", str(chunk_length_seconds),
            "-c", "copy",
            chunk_pattern,
        ]

        try:
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            chunk_files = sorted(
                [
                    os.path.join(work_dir, f)
                    for f in os.listdir(work_dir)
                    if f.startswith(f"{base_name}_chunk_") and f.endswith(".wav")
                ]
            )
            return chunk_files if chunk_files else [audio_path]
        except (subprocess.SubprocessError, FileNotFoundError) as exc:
            logger.warning(f"[AudioService] FFmpeg chunking skipped or failed: {exc}. Using original file.")
            return [audio_path]
