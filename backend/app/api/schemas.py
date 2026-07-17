"""Pydantic request/response models for the REST API."""
from pydantic import BaseModel, Field


class ConverseResponse(BaseModel):
    """Response returned by POST /api/converse."""

    session_id: str
    transcript: str = Field(..., description="What the STT engine heard the user say.")
    reply_text: str = Field(..., description="The LLM's textual reply.")
    llm_provider_used: str = Field(..., description="Which LLM provider produced the reply.")
    tts_provider_used: str = Field(..., description="Which TTS provider synthesized the audio.")
    audio_url: str = Field(..., description="URL the frontend should fetch to play the reply audio.")
    latency_ms: dict[str, float] = Field(..., description="Per-stage latency breakdown.")
    used_fallback_filler: bool = Field(
        default=False, description="True if a filler phrase was needed before the real reply."
    )


class ClearSessionRequest(BaseModel):
    session_id: str


class HealthResponse(BaseModel):
    status: str
    app_name: str
    stt_ready: bool
    llm_provider: str
    tts_provider: str


class ErrorResponse(BaseModel):
    detail: str
