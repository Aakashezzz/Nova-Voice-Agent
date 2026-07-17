"""
Groq-hosted Whisper STT provider.

Uses Groq's OpenAI-compatible audio transcription endpoint (Whisper
large-v3 running on Groq's LPU hardware) instead of a local model. This
trades "fully offline" for meaningfully better accuracy and zero local
model management, at the cost of needing network access and a Groq API
key. It also skips the local decode/trim/normalize pipeline entirely --
Groq accepts webm/mp3/wav/m4a directly and handles its own preprocessing.
"""
import logging

from groq import AsyncGroq

from app.core.config import get_settings
from app.core.exceptions import STTError

logger = logging.getLogger(__name__)


class GroqSTT:
    """Speech-to-text via Groq's hosted Whisper large-v3 endpoint."""

    def __init__(self) -> None:
        settings = get_settings()
        if not settings.groq_api_key:
            raise STTError("GROQ_API_KEY is not set; cannot use the Groq STT provider.")
        self._client = AsyncGroq(api_key=settings.groq_api_key)
        self.model = settings.groq_stt_model

    async def transcribe(self, raw_bytes: bytes, filename: str = "utterance.webm") -> str:
        """Transcribe raw audio bytes (webm/mp3/wav/m4a) via the Groq API."""
        if not raw_bytes:
            raise STTError("Received empty audio buffer for transcription.")
        try:
            response = await self._client.audio.transcriptions.create(
                file=(filename, raw_bytes),
                model=self.model,
                language="en",
                response_format="text",
            )
            text = response if isinstance(response, str) else getattr(response, "text", "")
            return text.strip()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Groq STT failed: %s", exc)
            raise STTError(f"Groq STT provider failed: {exc}") from exc


_groq_stt_instance: GroqSTT | None = None


def get_groq_stt() -> GroqSTT:
    global _groq_stt_instance
    if _groq_stt_instance is None:
        _groq_stt_instance = GroqSTT()
    return _groq_stt_instance