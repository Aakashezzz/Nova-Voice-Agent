# Latency Optimization Notes

Target: **under 2 seconds** end-to-end, whenever possible, on CPU-only
hardware.

## Where the time goes (typical CPU-only breakdown)

| Stage | Typical time | Main lever |
|-------|-------------|------------|
| Audio decode | 20-60ms | Negligible; `pydub`/ffmpeg is fast for short clips |
| STT (Whisper) | 200-600ms | Model size, `beam_size`, CPU thread count |
| LLM | 300-1200ms | Model size, prompt/history length, provider |
| TTS (Piper) | 150-400ms | Model size (Piper is already fast on CPU) |

## Optimizations applied

1. **Models load once, not per-request.** `WhisperSTT`, `PiperTTS`, and
   the VAD model are all module-level singletons instantiated lazily on
   first use, then reused for the process lifetime. Reloading a Whisper
   model per-request would add hundreds of ms every time.
2. **Greedy decoding for Whisper (`beam_size=1`).** Beam search improves
   accuracy marginally but multiplies decode time; for a conversational
   assistant, greedy decoding is the right trade-off.
3. **`.en`-suffixed, smaller Whisper models by default.** English-only
   models skip multilingual detection overhead. `base.en` is the default;
   `tiny.en` is available for even lower latency on weaker hardware.
4. **Bounded conversation history.** `LLM_MAX_HISTORY_TURNS` caps how
   much context gets sent to the LLM each turn — unbounded history would
   silently grow prompt-processing time as a conversation gets longer.
5. **int8 quantization for Whisper** (`WHISPER_COMPUTE_TYPE=int8`) trades
   a small amount of accuracy for meaningfully faster CPU inference.
6. **Client-side silence detection** avoids a network round-trip to
   decide when the user has stopped talking, so recording ends the moment
   they go quiet rather than after a fixed timer.
7. **Async I/O throughout the LLM/TTS network calls** (`httpx.AsyncClient`,
   `async def` providers) so the event loop isn't blocked while waiting
   on Ollama/Groq/edge-tts.

## Where latency is intentionally traded for simplicity

- **No token streaming.** Streaming Ollama's output token-by-token into
  incremental TTS synthesis would lower *perceived* latency (time to
  first audio) further, but adds real complexity (chunk-boundary
  handling, partial-sentence TTS, WebSocket lifecycle). Given the
  explicit "don't over-engineer" instruction and that small local models
  already land comfortably under 2s for short conversational replies,
  this was left for a documented future improvement rather than built now.
- **No GPU-specific tuning.** `WHISPER_DEVICE=cuda` is supported and will
  speed things up substantially if you have a GPU, but no CUDA-specific
  code paths were added beyond what faster-whisper/torch already handle.

## If you need to go faster

- Swap to `tiny.en` Whisper and a 1B-parameter Ollama model.
- Move Ollama to a GPU-equipped machine.
- Skip the fallback filler delay tuning (`FILLER_AFTER_SECONDS`) down if
  you'd rather show a filler sooner during genuinely slow responses.
