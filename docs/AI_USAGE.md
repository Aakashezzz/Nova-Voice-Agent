# AI Usage Report

In the interest of full transparency, this document details where and how
AI assistance was used in building this project.

## Where AI was used

| Area | How it was used |
|------|------------------|
| Project planning | Used AI to translate the assignment brief into a concrete architecture (pipeline stages, folder structure, tech stack choices) before writing any code. |
| Architecture brainstorming | Discussed trade-offs (REST vs. WebSocket streaming, database vs. in-memory conversation history, offline vs. online providers) with AI to settle on a "simplest architecture that satisfies every requirement" approach. |
| Code generation | AI generated the full initial implementation across backend (FastAPI app, STT/LLM/TTS/VAD wrappers, fallback logic, conversation manager) and frontend (React components, hooks, API client). |
| Documentation drafting | README, Architecture doc, Installation guide, Testing guide, Deployment guide, Troubleshooting guide, and Latency notes were all AI-drafted based on the actual implementation, then reviewed. |
| Debugging assistance | Used AI to reason through error handling and fallback edge cases (e.g. what happens if Ollama is down, if Piper models are missing, if all LLM providers fail). |
| Testing assistance | AI wrote the pytest test suite (conversation manager, fallback manager, audio store, LLM manager fallback ordering, basic API health checks) and explained why full end-to-end pipeline tests were left as a manual/documented step rather than automated (heavy model downloads). |
| README / docs writing | All markdown documentation in `docs/` was AI-authored from the implementation, not the other way around — code was written first, docs describe what was actually built. |

## What was NOT done by AI

- Running the actual voice pipeline end-to-end with a live microphone and
  speaker (this requires local hardware access this environment doesn't have).
- Downloading and validating the real Whisper/Piper model weights at
  runtime, or confirming the app runs error-free on your specific machine.
- Any human review, testing on real hardware, and validation of the
  generated code should be done by the person submitting this project
  before treating it as final/submission-ready.

## Why this document exists

The assignment explicitly required transparency about AI usage rather
than hiding it. This project was built with heavy AI code-generation
assistance from an initial detailed brief; the resulting code should be
reviewed, run, and tested locally before being presented as personally
verified work.
