# Deployment Guide

This project ships as an MVP intended primarily for local/demo use. If you
want to deploy it beyond localhost, here's the straightforward path.

## Backend

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
```

Notes:
- Keep `--workers 1` unless you refactor the STT/TTS singletons to be
  process-safe — each worker process would otherwise load its own copy
  of the Whisper/Piper models, multiplying memory use.
- Set `DEBUG=false` and a restrictive `CORS_ORIGINS` in `.env` for any
  non-local deployment.
- If deploying to a machine without a local Ollama instance, set
  `LLM_PROVIDER_PRIMARY=groq` and provide `GROQ_API_KEY`.
- Behind a reverse proxy (nginx/Caddy), make sure request bodies up to a
  few MB are allowed (recorded utterances) and that `/api/*` is proxied
  to the FastAPI process.

## Frontend

```bash
cd frontend
npm run build
```

This produces static files in `frontend/dist/` that can be served by any
static host (nginx, Vercel, Netlify, S3+CloudFront, etc). Update the
`/api` proxy target — in production, either:

- Serve the frontend from the same origin as the backend and reverse-proxy `/api/*` to FastAPI, or
- Set an absolute API base URL via an environment variable and update `src/api.ts` accordingly.

## Containerizing (optional)

A single `docker-compose.yml` with two services (backend, frontend) is
sufficient here — deliberately not Kubernetes/Swarm, per the project's
"keep it simple" requirement. A minimal backend Dockerfile:

```dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Mount your downloaded Piper models as a volume rather than baking them
into the image, since voice files are large and may change independently
of app code.

## Environment Checklist for Production

- [ ] `.env` reviewed — no secrets committed
- [ ] `CORS_ORIGINS` restricted to your actual frontend domain
- [ ] `GROQ_API_KEY` set if relying on the online LLM fallback
- [ ] HTTPS terminated at the reverse proxy (browsers require secure
      contexts for `getUserMedia` microphone access, except on `localhost`)
