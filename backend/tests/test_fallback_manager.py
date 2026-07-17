"""Unit tests for the fallback filler manager."""
from app.fallback.filler_manager import (
    THINKING_FILLERS,
    get_apologetic_fallback,
    get_listening_filler,
    get_thinking_filler,
)


def test_thinking_filler_returns_known_phrase():
    assert get_thinking_filler() in THINKING_FILLERS


def test_listening_filler_returns_nonempty_string():
    phrase = get_listening_filler()
    assert isinstance(phrase, str)
    assert len(phrase) > 0


def test_apologetic_fallback_is_polite_and_stable():
    message = get_apologetic_fallback()
    assert "sorry" not in message.lower() or "trouble" in message.lower()
    # Should be deterministic (not randomly chosen) so tests/UX stay predictable.
    assert message == get_apologetic_fallback()
