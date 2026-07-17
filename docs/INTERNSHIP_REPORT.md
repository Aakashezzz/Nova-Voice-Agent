# Internship Project Report

## Real-Time Audio-In Audio-Out Conversational AI Assistant

---

## 1. Project Overview

This project implements a real-time, voice-driven conversational AI
assistant. A user speaks into their microphone; the system detects when
they've finished talking, transcribes their speech, generates an
intelligent conversational reply using a large language model, converts
that reply back into natural-sounding speech, and plays it automatically
— aiming to feel like a smooth, low-latency conversation rather than a
request/response chatbot.

## 2. Objective

Build an assistant that:
- Accepts microphone input and detects speech start/stop automatically
- Converts speech to text and text back to speech
- Maintains conversational context across turns
- Responds within roughly 2 seconds whenever possible
- Never leaves the user staring at silence or a generic error — uses
  natural filler phrases instead
- Runs offline-first, with online services as a graceful fallback

## 3. Requirements

**Functional:** microphone capture, voice activity detection, speech-to-text,
LLM-based reply generation, text-to-speech, automatic playback, multi-turn
memory, graceful handling of slow/failed stages.

**Non-functional:** modular codebase with clear separation of concerns,
production-style error handling and logging, no unnecessary infrastructure
(no Redis/Kafka/Kubernetes/microservices), readable and extensible code.

## 4. System Design

The system is a single FastAPI backend plus a React frontend, communicating
over one REST endpoint per conversational turn (`POST /api/converse`).
Each internal capability (VAD, STT, LLM, TTS, conversation memory, fallback
logic) is isolated into its own module with a narrow, typed interface, so
any one piece (e.g. swapping Ollama for a different local LLM) can change
without touching the rest of the system.

See [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) for the full pipeline diagram,
request lifecycle, and data flow.

## 5. Architecture Summary

```
Microphone → Client-side VAD → Upload → Decode Audio → Whisper STT
  → Conversation Manager → LLM Manager (Ollama → Groq fallback)
  → TTS Manager (Piper → edge-tts fallback) → Audio Store → Playback
```

Design priorities, in order: correctness of the core loop, graceful
degradation when any single dependency is unavailable, and low latency
through singleton model loading, bounded conversation history, and
greedy/lightweight model configurations.

## 6. Implementation

- **Backend**: Python 3.11, FastAPI, Faster-Whisper, Silero VAD, Piper TTS,
  edge-tts, Ollama/Groq clients. Fully typed with docstrings, structured
  logging, and a custom exception hierarchy (`AssistantError` and subclasses)
  so failures are caught and handled predictably rather than crashing the
  request.
- **Frontend**: React + TypeScript + Tailwind CSS. A `useAudioRecorder` hook
  handles microphone capture and client-side silence detection; a
  `useVoiceAssistant` hook orchestrates the assistant's state machine
  (idle → listening → processing → speaking) and manages the filler-phrase
  timer, transcript, and session id.
- **Conversation memory**: in-memory, per-session, sliding-window history —
  intentionally not backed by a database, since persistence beyond a
  browser session wasn't a stated requirement.

## 7. Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| Deciding when the user has stopped talking, without a slow server round-trip | Client-side silence detection via the Web Audio API `AnalyserNode`, tuned to ~900ms of near-silence |
| Keeping the assistant from ever going silent during a slow LLM/network call | A filler-phrase timer in the frontend shows a natural "thinking" message if processing exceeds ~1.2s, replaced seamlessly once the real reply arrives |
| Avoiding a single point of failure on any one external service | Every external dependency (LLM, TTS) has an automatic fallback provider, tried transparently without surfacing an error to the user unless everything fails |
| Keeping the codebase simple per the assignment's explicit instruction | No database, no message queue, no microservices — a single FastAPI process with clearly separated internal modules |

## 8. Testing

Unit tests cover the conversation manager (session isolation, history
trimming), fallback filler logic, the in-memory audio store, and LLM
provider fallback ordering (using fake providers so tests don't require
live network/model access). Full end-to-end pipeline testing (real audio
in, real audio out) is documented as a manual step in
[`docs/TESTING.md`](TESTING.md), since it depends on downloading real
model weights that aren't practical to bundle into automated CI by
default.

## 9. Results

The architecture meets every functional requirement in the assignment:
voice in, intelligent reply, voice out, multi-turn memory, and graceful
fallback behavior at every external dependency boundary. Latency depends
on hardware (CPU vs GPU, model sizes chosen), documented in
[`docs/LATENCY_NOTES.md`](LATENCY_NOTES.md) along with the specific
optimizations applied to stay near the 2-second target on CPU-only setups.

## 10. Future Improvements

- WebSocket-based token streaming for lower perceived latency (speaking
  the beginning of a reply while the rest is still generating)
- True interruption/barge-in support mid-playback
- Optional persisted history for returning users
- Multi-language support across STT and TTS

## 11. Conclusion

This project demonstrates an end-to-end, production-style approach to
building a real-time voice assistant: a clear pipeline, sensible
defaults, graceful degradation, and documentation written to match what
was actually implemented rather than what was merely planned. The
codebase is intentionally scoped to avoid unnecessary infrastructure
while remaining straightforward to extend — e.g., swapping in streaming
responses or persistent memory later without restructuring the project.
