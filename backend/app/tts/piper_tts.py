"""
Text-to-Speech using Piper (offline, on-device neural TTS).

Piper is fast enough to run on CPU in near real-time, which is why it's
the primary choice for keeping the whole pipeline offline-capable.
Voice model files (.onnx + .onnx.json) must be downloaded once and placed
under backend/models/piper/ (see docs/INSTALLATION.md).
"""
import io
import logging
import wave
from pathlib import Path

from piper import PiperVoice

from app.core.config import get_settings
from app.core.exceptions import TTSError

logger = logging.getLogger(__name__)


class PiperTTS:
    """Wraps a local Piper voice model for text-to-speech synthesis."""

    def __init__(self) -> None:
        settings = get_settings()
        model_path = Path(settings.piper_model_path)
        config_path = Path(settings.piper_config_path)

        if not model_path.exists() or not config_path.exists():
            raise TTSError(
                f"Piper voice model not found at '{model_path}'. "
                "Download a voice from https://github.com/rhasspy/piper/releases "
                "and place it under backend/models/piper/ (see INSTALLATION.md)."
            )

        logger.info("Loading Piper voice model '%s'...", model_path.name)
        self._voice = PiperVoice.load(str(model_path), config_path=str(config_path))
        logger.info("Piper voice model loaded.")

    def synthesize(self, text: str) -> bytes:
        """Synthesize `text` into WAV audio bytes."""
        if not text.strip():
            raise TTSError("Cannot synthesize empty text.")

        try:
            buffer = io.BytesIO()
            with wave.open(buffer, "wb") as wav_file:
                self._voice.synthesize(text, wav_file)
            return buffer.getvalue()
        except Exception as exc:  # noqa: BLE001
            raise TTSError(f"Piper synthesis failed: {exc}") from exc


_piper_instance: PiperTTS | None = None


def get_piper_tts() -> PiperTTS:
    global _piper_instance
    if _piper_instance is None:
        _piper_instance = PiperTTS()
    return _piper_instance
