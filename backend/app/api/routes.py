"""
API routes.

POST /api/converse   - core pipeline: audio in -> transcript, reply, reply audio URL
GET  /api/audio/{id} - fetch synthesized reply audio
POST /api/clear       - clear a session's conversation history
GET  /api/health      - readiness/liveness probe
"""
import logging
import uuid

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response

from app.api.audio_store import get_audio_store
from app.api.schemas import ClearSessionRequest, ConverseResponse, HealthResponse
from app.conversation.manager import get_conversation_manager
from app.core.config import get_settings
from app.core.exceptions import LLMError, STTError, TTSError
from app.fallback.filler_manager import get_apologetic_fallback
from app.llm.llm_manager import get_llm_manager
from app.stt.stt_manager import get_stt_manager
from app.tts.tts_manager import get_tts_manager
from app.utils.timing import StageTimings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["conversation"])


@router.post("/converse", response_model=ConverseResponse)
async def converse(
    audio: UploadFile = File(..., description="Recorded user utterance (webm/wav/ogg)."),
    session_id: str | None = Form(default=None),
) -> ConverseResponse:
    """
    Run the full pipeline for one conversational turn:
    audio -> STT -> conversation history -> LLM -> TTS -> audio URL.
    """
    session_id = session_id or uuid.uuid4().hex
    timings = StageTimings()
    used_fallback_filler = False

    # --- Transcribe (local Whisper or Groq API, per STT_PROVIDER_PRIMARY) ---
    try:
        raw_bytes = await audio.read()
        with timings.track("stt"):
            transcript = await get_stt_manager().transcribe(raw_bytes, filename=audio.filename or "utterance.webm")

        if not transcript.strip():
            raise HTTPException(status_code=422, detail="No speech detected in the provided audio.")

    except STTError as exc:
        logger.error("STT stage failed: %s", exc)
        raise HTTPException(status_code=502, detail=f"Speech recognition failed: {exc}") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # --- Conversation history + LLM ---
    conv_manager = get_conversation_manager()
    conv_manager.add_turn(session_id, "user", transcript)

    try:
        with timings.track("llm"):
            history = conv_manager.get_history(session_id)
            reply_text, llm_provider_used = await get_llm_manager().generate_reply(history)
    except LLMError as exc:
        logger.error("All LLM providers failed: %s", exc)
        used_fallback_filler = True
        reply_text = get_apologetic_fallback()
        llm_provider_used = "fallback"

    conv_manager.add_turn(session_id, "assistant", reply_text)

    # --- TTS ---
    try:
        with timings.track("tts"):
            audio_bytes, mime_type, tts_provider_used = await get_tts_manager().synthesize(reply_text)
    except TTSError as exc:
        logger.error("All TTS providers failed: %s", exc)
        raise HTTPException(status_code=502, detail=f"Speech synthesis failed: {exc}") from exc

    audio_id = get_audio_store().put(audio_bytes, mime_type)

    return ConverseResponse(
        session_id=session_id,
        transcript=transcript,
        reply_text=reply_text,
        llm_provider_used=llm_provider_used,
        tts_provider_used=tts_provider_used,
        audio_url=f"/api/audio/{audio_id}",
        latency_ms=timings.as_dict(),
        used_fallback_filler=used_fallback_filler,
    )


@router.get("/audio/{audio_id}")
async def get_audio(audio_id: str) -> Response:
    """Serve previously synthesized reply audio by its id."""
    entry = get_audio_store().get(audio_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Audio not found or expired.")
    return Response(content=entry.data, media_type=entry.mime_type)


@router.post("/clear")
async def clear_session(payload: ClearSessionRequest) -> dict[str, str]:
    """Clear a session's conversation history (the 'Clear Conversation' button)."""
    get_conversation_manager().clear(payload.session_id)
    return {"status": "cleared", "session_id": payload.session_id}


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Basic readiness probe used by the frontend's connection status indicator."""
    settings = get_settings()
    stt_ready = True
    try:
        if settings.stt_provider_primary == "local":
            from app.stt.whisper_stt import get_stt

            get_stt()
        # Groq STT readiness isn't checked eagerly here (no local model to
        # load); a missing API key will surface on the first real request.
    except Exception:  # noqa: BLE001
        stt_ready = False

    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        stt_ready=stt_ready,
        llm_provider=settings.llm_provider_primary,
        tts_provider=settings.tts_provider_primary,
    )