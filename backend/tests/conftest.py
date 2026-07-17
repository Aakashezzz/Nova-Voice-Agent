"""Shared pytest fixtures."""
import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture()
def silence_audio() -> np.ndarray:
    """One second of digital silence at 16kHz, for VAD/STT edge-case tests."""
    return np.zeros(16_000, dtype=np.float32)


@pytest.fixture()
def synthetic_tone() -> np.ndarray:
    """A simple sine tone — not speech, but useful for shape/format tests."""
    t = np.linspace(0, 1, 16_000, endpoint=False)
    return (0.1 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
