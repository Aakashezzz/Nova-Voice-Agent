"""
Application configuration.

Centralised, typed settings loaded from environment variables (.env).
Using pydantic-settings keeps configuration validated and IDE-friendly,
and avoids scattering os.getenv() calls throughout the codebase.
"""
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the Audio-In Audio-Out assistant."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- App ---
    app_name: str = "Realtime Voice Assistant"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

   # --- STT (Speech To Text) ---
    stt_provider_primary: Literal["local", "groq"] = "local"
    whisper_model_size: str = "base.en"  # tiny/base/small/medium; .en = English-only, faster
    whisper_device: Literal["cpu", "cuda"] = "cpu"
    whisper_compute_type: str = "int8"  # int8 is fastest on CPU
    groq_stt_model: str = "whisper-large-v3"

    # --- VAD (Voice Activity Detection) ---
    vad_threshold: float = 0.5
    vad_min_silence_ms: int = 700  # silence duration that ends an utterance

    # --- LLM ---
    llm_provider_primary: Literal["ollama", "groq"] = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    llm_timeout_seconds: float = 6.0  # after this, fallback filler kicks in
    llm_max_history_turns: int = 10  # sliding window of conversation memory

    # --- TTS (Text To Speech) ---
    tts_provider_primary: Literal["piper", "online"] = "piper"
    piper_model_path: str = "models/piper/en_US-lessac-medium.onnx"
    piper_config_path: str = "models/piper/en_US-lessac-medium.onnx.json"

    # --- Fallback / UX ---
    filler_after_seconds: float = 1.2  # how long to wait before playing a filler phrase
    max_response_wait_seconds: float = 8.0

    # --- Logging ---
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (loaded once per process)."""
    return Settings()
