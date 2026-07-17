# VoiceAssistant — Real-Time Audio-In Audio-Out Conversational AI

A production-style, real-time voice assistant: speak into your microphone,
and it listens, thinks, and talks back — with graceful conversational
fillers instead of silence or spinners while it works.

```
🎙️  You speak  →  🧠 It understands  →  💬 It replies  →  🔊 It speaks back
```

## Highlights

- **Under 2s target latency** end-to-end (STT → LLM → TTS)
- **Offline-first**: Faster-Whisper + Piper TTS + Ollama run entirely on-device
- **Graceful online fallback**: Groq (LLM) and edge-tts (TTS) kick in automatically if the offline path fails or isn't set up
- **Never leaves you waiting silently**: natural filler phrases ("Let me think about that...") appear instead of a blank spinner
- **Clean, modular architecture** — see [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)

## Tech Stack

| Layer      | Choice                                    |
|------------|--------------------------------------------|
| Backend    | Python 3.11+, FastAPI                      |
| Frontend   | React + Vite + TypeScript + Tailwind CSS   |
| STT        | Faster-Whisper                             |
| VAD        | Silero VAD                                 |
| LLM        | Ollama (offline) → Groq (fallback)         |
| TTS        | Piper (offline) → edge-tts (fallback)      |
| Memory     | In-memory, per-session (no database)       |

## Quick Start

See [`docs/INSTALLATION.md`](docs/INSTALLATION.md) for full setup. Short version:

```bash
# 1. Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000

# 2. Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`, allow microphone access, and start talking.

## Project Structure

```
project/
├── backend/
│   ├── app/
│   │   ├── audio/          # audio decoding/format helpers
│   │   ├── vad/             # Silero VAD wrapper
│   │   ├── stt/              # Faster-Whisper wrapper
│   │   ├── llm/               # Ollama + Groq providers, fallback manager
│   │   ├── tts/                 # Piper + edge-tts providers, fallback manager
│   │   ├── conversation/         # in-memory session history
│   │   ├── fallback/              # filler-phrase manager
│   │   ├── api/                    # FastAPI routes, schemas, audio store
│   │   ├── core/                     # config, logging, exceptions
│   │   └── utils/                     # timing/latency helpers
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   └── src/
│       ├── components/    # MicOrb, TranscriptPanel, StatusBar
│       ├── hooks/          # useAudioRecorder, useVoiceAssistant
│       ├── api.ts
│       └── App.tsx
├── docs/                  # architecture, install, deploy, troubleshooting, reports
├── scripts/               # setup/run helper scripts
└── README.md
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md) — pipeline, data flow, design decisions
- [Installation](docs/INSTALLATION.md) — full setup including model downloads
- [Testing](docs/TESTING.md) — how to run the test suite
- [Deployment](docs/DEPLOYMENT.md) — running this beyond localhost
- [Troubleshooting](docs/TROUBLESHOOTING.md) — common issues and fixes
- [Latency Optimization Notes](docs/LATENCY_NOTES.md)
- [AI Usage Report](docs/AI_USAGE.md)
- [Internship Report](docs/INTERNSHIP_REPORT.md)

## Known Limitations

- Piper and Ollama model weights are not bundled (too large for source control) — see Installation guide to download them.
- The current pipeline is single-turn request/response (record → send → reply), not full-duplex streaming; see Architecture doc for the streaming upgrade path.
- No authentication/multi-user isolation beyond a per-browser session id — not intended for public deployment as-is.

## Future Improvements

- WebSocket streaming for token-by-token LLM output and lower time-to-first-audio
- True barge-in support (interrupt playback the instant the user starts speaking)
- Persisted conversation history (SQLite) for returning users, if genuinely needed
- Multi-language STT/TTS support
