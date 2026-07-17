"""Unit tests for the in-memory audio store."""
from app.api.audio_store import AudioStore


def test_put_and_get_roundtrip():
    store = AudioStore()
    audio_id = store.put(b"fake-wav-bytes", "audio/wav")

    entry = store.get(audio_id)
    assert entry is not None
    assert entry.data == b"fake-wav-bytes"
    assert entry.mime_type == "audio/wav"


def test_get_unknown_id_returns_none():
    store = AudioStore()
    assert store.get("does-not-exist") is None


def test_each_put_gets_unique_id():
    store = AudioStore()
    id1 = store.put(b"a", "audio/wav")
    id2 = store.put(b"b", "audio/wav")
    assert id1 != id2
