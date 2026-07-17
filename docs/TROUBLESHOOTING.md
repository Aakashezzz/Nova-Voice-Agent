# Troubleshooting Guide

## "Microphone access was denied or unavailable"

- Browsers require a secure context for `getUserMedia`: `http://localhost` is fine, but any other non-HTTPS origin will silently fail. Deploy behind HTTPS for anything beyond local dev.
- Check your OS-level microphone permissions for the browser itself (System Settings → Privacy → Microphone on macOS; Windows Settings → Privacy → Microphone).

## Backend fails to start: "Piper voice model not found"

Piper voices aren't bundled (too large for source control). Either:
- Download a voice per `docs/INSTALLATION.md` step 1b, or
- Set `TTS_PROVIDER_PRIMARY=online` in `.env` to skip Piper entirely and use edge-tts.

## Replies are slow (> 2s)

Check `latency_ms` in the API response (also shown in the frontend status bar) to see which stage is the bottleneck:
- **High `stt` time**: try a smaller Whisper model (`WHISPER_MODEL_SIZE=tiny.en`).
- **High `llm` time**: your Ollama model may be too large for your CPU/GPU — try a smaller model (e.g. `llama3.2:1b`) or switch to Groq (`LLM_PROVIDER_PRIMARY=groq`), which runs on dedicated inference hardware.
- **High `tts` time**: Piper is usually fast; if it's slow, confirm you're not accidentally falling back to edge-tts (check `tts_provider_used` in the response — network latency to Microsoft's servers adds overhead).

## "All LLM providers failed"

- Confirm Ollama is running: `curl http://localhost:11434/api/tags`
- Confirm the model is pulled: `ollama list`
- If relying on Groq as a fallback, confirm `GROQ_API_KEY` is set and valid.

## CORS errors in the browser console

Add your frontend's origin to `CORS_ORIGINS` in `backend/.env`, then
restart the backend (env vars are read once at startup).

## `ffmpeg` errors when decoding audio

`pydub` shells out to `ffmpeg`. Confirm it's installed and on your PATH:

```bash
ffmpeg -version
```

If missing, install it (see Installation guide's Prerequisites section).

## Whisper/Piper models download very slowly or fail

Both are pulled from external hosts on first use. If you're behind a
restrictive network/proxy, download the files manually ahead of time and
point `WHISPER_MODEL_SIZE`/`PIPER_MODEL_PATH` at local paths.

## Frontend shows "Offline" in the status bar

The status bar polls `GET /api/health` every 15s. If it shows Offline:
- Confirm the backend is running on the port the frontend expects (`vite.config.ts` proxies to `http://localhost:8000`).
- Check the backend terminal for startup errors.
