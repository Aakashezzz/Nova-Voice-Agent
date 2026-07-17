# Testing Guide

## Backend

```bash
cd backend
source .venv/bin/activate
pytest -v
```

### What's covered

| File | Covers |
|------|--------|
| `tests/test_conversation_manager.py` | Session isolation, history trimming, clearing |
| `tests/test_fallback_manager.py` | Filler phrase selection, apologetic fallback |
| `tests/test_audio_store.py` | In-memory audio caching/retrieval |
| `tests/test_llm_manager.py` | Provider fallback ordering, all-providers-fail case (uses fake providers, no real network calls) |
| `tests/test_api_health.py` | Root/clear/audio-404 endpoints |

### Why some tests are excluded from the default run

Full end-to-end `/api/converse` tests would require the real Whisper and
Piper model weights to be downloaded (multi-hundred-MB, and slow on CPU),
which isn't practical for a fast local test loop or CI by default. To
test the full pipeline manually once models are installed:

```bash
curl -X POST http://localhost:8000/api/converse \
  -F "audio=@sample.wav" \
  -F "session_id=manual-test"
```

Record a short `sample.wav` (e.g. via `ffmpeg -f avfoundation -i ":0" -t 3 sample.wav` on macOS) and confirm you get back a transcript, reply text, and a playable `audio_url`.

## Frontend

The frontend doesn't include automated tests in this MVP (per the
"avoid over-engineering" brief) — manual testing checklist:

- [ ] Mic button requests permission and starts listening
- [ ] Recording auto-stops after ~1s of silence
- [ ] "Thinking..." filler appears if the backend takes >1.2s
- [ ] Reply audio plays automatically
- [ ] Transcript shows both user and assistant turns, auto-scrolls
- [ ] "Clear conversation" empties the transcript and resets the session
- [ ] Status bar shows Connected/Offline correctly (try stopping the backend)
- [ ] Works on a narrow (mobile-width) viewport

If you'd like to add automated frontend tests later, Vitest + React
Testing Library is the natural fit given this Vite/React stack.
