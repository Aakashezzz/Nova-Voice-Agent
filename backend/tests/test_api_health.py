"""
API-level tests that don't require heavy ML models to be loaded.

Full end-to-end /api/converse tests are intentionally excluded here since
they require real Whisper/Piper model weights (see docs/TESTING.md for
how to run those manually / in CI with models cached).
"""


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_clear_session_endpoint(client):
    response = client.post("/api/clear", json={"session_id": "test-session"})
    assert response.status_code == 200
    assert response.json()["status"] == "cleared"


def test_audio_not_found_returns_404(client):
    response = client.get("/api/audio/does-not-exist")
    assert response.status_code == 404
