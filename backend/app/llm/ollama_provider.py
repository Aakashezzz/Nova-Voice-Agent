"""
Ollama LLM provider — the primary, fully offline inference path.

Requires a local Ollama server running (`ollama serve`) with the
configured model pulled beforehand (`ollama pull llama3.2:3b`).
"""
import logging

import httpx

from app.core.config import get_settings
from app.core.exceptions import LLMError
from app.llm.base import LLMProvider

logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    name = "ollama"

    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
        self.timeout = settings.llm_timeout_seconds

    async def generate(self, messages: list[dict[str, str]]) -> str:
        payload = {"model": self.model, "messages": messages, "stream": False}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/api/chat", json=payload)
                response.raise_for_status()
                data = response.json()
                return data["message"]["content"].strip()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Ollama generation failed: %s", exc)
            raise LLMError(f"Ollama provider failed: {exc}") from exc
