"""
TTS Manager.

Tries Piper (offline) first; falls back to edge-tts (online) if Piper
isn't set up or fails at runtime. Returns both the audio bytes and a
mime type, since Piper produces WAV and edge-tts produces MP3.
"""
import logging

from app.core.config import get_settings
from app.core.exceptions import TTSError
from app.tts.online_tts import get_online_tts
from app.tts.piper_tts import get_piper_tts

logger = logging.getLogger(__name__)


class TTSManager:
    """Coordinates offline/online TTS providers with graceful fallback."""

    def __init__(self) -> None:
        settings = get_settings()
        self.primary = settings.tts_provider_primary

    async def synthesize(self, text: str) -> tuple[bytes, str, str]:
        """
        Synthesize speech for `text`.

        Returns (audio_bytes, mime_type, provider_name_used).
        """
        if self.primary == "piper":
            try:
                piper = get_piper_tts()
                audio = piper.synthesize(text)
                return audio, "audio/wav", "piper"
            except TTSError as exc:
                logger.warning("Piper TTS unavailable (%s); falling back to online TTS.", exc)

        online = get_online_tts()
        audio = await online.synthesize(text)
        return audio, "audio/mpeg", "edge-tts"


_tts_manager_instance: TTSManager | None = None


def get_tts_manager() -> TTSManager:
    global _tts_manager_instance
    if _tts_manager_instance is None:
        _tts_manager_instance = TTSManager()
    return _tts_manager_instance
