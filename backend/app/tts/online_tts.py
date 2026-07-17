"""
Online TTS fallback using edge-tts (Microsoft Edge's free neural voices).

Used only when Piper is unavailable or fails (e.g. missing model files
on a fresh install), so the assistant can still speak while the user
finishes offline setup.
"""
import io
import logging

import edge_tts

from app.core.exceptions import TTSError

logger = logging.getLogger(__name__)

DEFAULT_VOICE = "en-US-AriaNeural"


class OnlineTTS:
    """Thin async wrapper around edge-tts for fallback speech synthesis."""

    def __init__(self, voice: str = DEFAULT_VOICE) -> None:
        self.voice = voice

    async def synthesize(self, text: str) -> bytes:
        """Synthesize `text` into MP3 audio bytes."""
        if not text.strip():
            raise TTSError("Cannot synthesize empty text.")

        try:
            communicator = edge_tts.Communicate(text, self.voice)
            audio_chunks = []
            async for chunk in communicator.stream():
                if chunk["type"] == "audio":
                    audio_chunks.append(chunk["data"])
            buffer = io.BytesIO()
            for chunk in audio_chunks:
                buffer.write(chunk)
            return buffer.getvalue()
        except Exception as exc:  # noqa: BLE001
            raise TTSError(f"Online TTS synthesis failed: {exc}") from exc


_online_tts_instance: OnlineTTS | None = None


def get_online_tts() -> OnlineTTS:
    global _online_tts_instance
    if _online_tts_instance is None:
        _online_tts_instance = OnlineTTS()
    return _online_tts_instance
