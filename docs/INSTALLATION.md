# Installation Guide

## Prerequisites

- Python 3.11+
- Node.js 18+
- `ffmpeg` on your PATH (used by `pydub` to decode browser audio)
  - macOS: `brew install ffmpeg`
  - Ubuntu/Debian: `sudo apt install ffmpeg`
  - Windows: `choco install ffmpeg` or download from ffmpeg.org
- [Ollama](https://ollama.com) installed, for fully offline LLM inference (optional but recommended)

## 1. Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

### 1a. Pull an Ollama model (offline LLM)

```bash
ollama pull llama3.2:3b
ollama serve   # if not already running as a background service
```

If you'd rather skip Ollama entirely, set `LLM_PROVIDER_PRIMARY=groq` in
`.env` and provide a `GROQ_API_KEY` (get one at https://console.groq.com).

### 1b. Download a Piper voice (offline TTS)

Piper voices are downloaded separately from the `piper-tts` pip package:

```bash
mkdir -p models/piper
cd models/piper
curl -LO https://github.com/rhasspy/piper/releases/download/v1.2.0/voice-en-us-lessac-medium.tar.gz
tar -xzf voice-en-us-lessac-medium.tar.gz
# You should now have en_US-lessac-medium.onnx and en_US-lessac-medium.onnx.json
cd ../..
```

If you skip this step, the app automatically falls back to `edge-tts`
(online, no API key required) — no crash, just a log warning.

### 1c. Run the backend

```bash
uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` to confirm the API is up (Swagger UI).
The first request will take longer than usual as Whisper/Piper models
load into memory; subsequent requests are fast.

## 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173`. The Vite dev server proxies `/api/*` to
`http://localhost:8000` (see `vite.config.ts`), so both servers must be
running.

## 3. First Conversation

1. Click the mic button and allow microphone access when prompted.
2. Speak a sentence; recording stops automatically after you go quiet.
3. Watch the status change: Listening → Thinking → Speaking.
4. The assistant's reply plays automatically.

## Verifying Everything Works

```bash
curl http://localhost:8000/api/health
```

Expected response:

```json
{
  "status": "ok",
  "app_name": "Realtime Voice Assistant",
  "stt_ready": true,
  "llm_provider": "ollama",
  "tts_provider": "piper"
}
```

If `stt_ready` is `false`, check the backend logs — the Whisper model
likely failed to download (first run needs internet access once).
