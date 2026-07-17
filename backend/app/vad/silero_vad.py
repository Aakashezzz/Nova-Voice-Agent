"""
Voice Activity Detection using Silero VAD.

Silero VAD is a small, fast, CPU-friendly model that decides whether a
chunk of audio contains speech. We use it to detect utterance boundaries
so we know when the user has finished talking, without relying on a
fixed silence timeout that would feel unnatural.

The model is loaded once (singleton) and reused for every request, since
loading it repeatedly would add unnecessary latency.
"""
import logging

import numpy as np
import torch

from app.core.config import get_settings
from app.core.exceptions import VADError

logger = logging.getLogger(__name__)

_SAMPLE_RATE = 16_000


class SileroVAD:
    """Thin wrapper around the torch.hub Silero VAD model."""

    def __init__(self) -> None:
        settings = get_settings()
        self.threshold = settings.vad_threshold
        self.min_silence_ms = settings.vad_min_silence_ms
        self._model = None
        self._get_speech_timestamps = None

    def _ensure_loaded(self) -> None:
        """Lazily load the model on first use (keeps startup fast)."""
        if self._model is not None:
            return
        try:
            logger.info("Loading Silero VAD model...")
            model, utils = torch.hub.load(
                repo_or_dir="snakers4/silero-vad",
                model="silero_vad",
                trust_repo=True,
                onnx=False,
            )
            self._model = model
            self._get_speech_timestamps = utils[0]
            logger.info("Silero VAD model loaded.")
        except Exception as exc:  # noqa: BLE001
            raise VADError(f"Failed to load Silero VAD model: {exc}") from exc

    def contains_speech(self, audio: np.ndarray, sample_rate: int = _SAMPLE_RATE) -> bool:
        """Return True if the given mono float32 PCM buffer contains speech."""
        self._ensure_loaded()
        try:
            tensor = torch.from_numpy(audio).float()
            timestamps = self._get_speech_timestamps(
                tensor,
                self._model,
                sampling_rate=sample_rate,
                threshold=self.threshold,
            )
            return len(timestamps) > 0
        except Exception as exc:  # noqa: BLE001
            raise VADError(f"VAD inference failed: {exc}") from exc

    def get_speech_segments(self, audio: np.ndarray, sample_rate: int = _SAMPLE_RATE) -> list[dict]:
        """Return start/end sample indices of speech segments within `audio`."""
        self._ensure_loaded()
        tensor = torch.from_numpy(audio).float()
        return self._get_speech_timestamps(
            tensor,
            self._model,
            sampling_rate=sample_rate,
            threshold=self.threshold,
            min_silence_duration_ms=self.min_silence_ms,
        )


# Module-level singleton so the model is loaded exactly once per process.
_vad_instance: SileroVAD | None = None


def get_vad() -> SileroVAD:
    global _vad_instance
    if _vad_instance is None:
        _vad_instance = SileroVAD()
    return _vad_instance
