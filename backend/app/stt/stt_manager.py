"""
STT Manager.

Chooses between the local Faster-Whisper model and Groq's hosted Whisper
API based on `STT_PROVIDER_PRIMARY`, so the rest of the app (routes.py)
doesn't need to know which one is active. The two paths take different
inputs (decoded 16kHz PCM vs raw uploaded bytes), so this manager also
owns the local decode step -- Groq handles its own audio decoding.
"""
import logging

from app.audio.audio_utils import decode_audio_bytes
from app.core.config import get_settings
from app.core.exceptions import STTError
from app.stt.groq_stt import get_groq_stt
from app.stt.whisper_stt import get_stt

logger = logging.getLogger(__name__)


class STTManager:
    def __init__(self) -> None:
        self.primary = get_settings().stt_provider_primary

    async def transcribe(self, raw_bytes: bytes, filename: str = "utterance.webm") -> str:
        """Transcribe raw uploaded audio bytes, using whichever provider is configured."""
        if self.primary == "groq":
            try:
                return await get_groq_stt().transcribe(raw_bytes, filename=filename)
            except STTError as exc:
                logger.warning("Groq STT failed (%s); falling back to local Whisper.", exc)

        pcm = decode_audio_bytes(raw_bytes)
        return get_stt().transcribe(pcm)


_stt_manager_instance: STTManager | None = None


def get_stt_manager() -> STTManager:
    global _stt_manager_instance
    if _stt_manager_instance is None:
        _stt_manager_instance = STTManager()
    return _stt_manager_instance