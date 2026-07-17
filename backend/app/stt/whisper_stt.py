"""
Speech-to-Text using Faster-Whisper.

Faster-Whisper (CTranslate2 backend) gives a significant speed-up over
vanilla openai-whisper on CPU, which matters for our <2s latency target.
The model is loaded once and reused across requests.
"""
import logging
import time

import numpy as np
from faster_whisper import WhisperModel

from app.core.config import get_settings
from app.core.exceptions import STTError

logger = logging.getLogger(__name__)


class WhisperSTT:
    """Wraps a Faster-Whisper model for one-shot utterance transcription."""

    def __init__(self) -> None:
        settings = get_settings()
        logger.info(
            "Loading Whisper model '%s' (device=%s, compute=%s)...",
            settings.whisper_model_size,
            settings.whisper_device,
            settings.whisper_compute_type,
        )
        self._model = WhisperModel(
            settings.whisper_model_size,
            device=settings.whisper_device,
            compute_type=settings.whisper_compute_type,
        )
        logger.info("Whisper model loaded.")

    def transcribe(self, audio: np.ndarray, sample_rate: int = 16_000) -> str:
        """Transcribe a mono float32 PCM buffer and return the text."""
        if audio.size == 0:
            raise STTError("Received empty audio buffer for transcription.")

        start = time.perf_counter()
        try:
            segments, info = self._model.transcribe(
                audio,
                language="en",
                vad_filter=False,  # extra safety net; Silero already gates upstream
                beam_size=5,      # greedy decoding: fastest, good enough for chat
            )
            text = " ".join(segment.text.strip() for segment in segments).strip()
        except Exception as exc:  # noqa: BLE001
            raise STTError(f"Transcription failed: {exc}") from exc

        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info("Transcribed %d samples in %.2fms -> '%s'", audio.size, elapsed_ms, text[:80])
        return text


# Module-level singleton — loading Whisper repeatedly would be far too slow.
_stt_instance: WhisperSTT | None = None


def get_stt() -> WhisperSTT:
    global _stt_instance
    if _stt_instance is None:
        _stt_instance = WhisperSTT()
    return _stt_instance
