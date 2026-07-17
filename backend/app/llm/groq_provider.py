"""
Groq LLM provider — the online fallback path.

Used when Ollama is unavailable or too slow (e.g. no local GPU).
Groq's LPU inference is fast enough to keep us within the latency budget.
"""
import logging

from groq import AsyncGroq

from app.core.config import get_settings
from app.core.exceptions import LLMError
from app.llm.base import LLMProvider

logger = logging.getLogger(__name__)


class GroqProvider(LLMProvider):
    name = "groq"

    def __init__(self) -> None:
        settings = get_settings()
        if not settings.groq_api_key:
            logger.warning("GROQ_API_KEY is not set; Groq fallback will be unavailable.")
        self._client = AsyncGroq(api_key=settings.groq_api_key) if settings.groq_api_key else None
        self.model = settings.groq_model
        self.timeout = settings.llm_timeout_seconds

    async def generate(self, messages: list[dict[str, str]]) -> str:
        if self._client is None:
            raise LLMError("Groq provider is not configured (missing GROQ_API_KEY).")
        try:
            response = await self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                timeout=self.timeout,
            )
            return response.choices[0].message.content.strip()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Groq generation failed: %s", exc)
            raise LLMError(f"Groq provider failed: {exc}") from exc
