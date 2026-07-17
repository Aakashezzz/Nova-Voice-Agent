"""
LLM Manager.

Orchestrates the primary/fallback LLM providers so the rest of the app
never has to know whether it's talking to Ollama or Groq. If the primary
provider fails or errors out, we transparently retry with the fallback.
"""
import logging

from app.core.config import get_settings
from app.core.exceptions import LLMError
from app.llm.base import LLMProvider
from app.llm.groq_provider import GroqProvider
from app.llm.ollama_provider import OllamaProvider

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a helpful, friendly voice assistant. Keep replies conversational, "
    "concise (2-4 sentences unless asked for detail), and natural to speak aloud. "
    "Avoid markdown, bullet points, or formatting that doesn't make sense in speech."
)


class LLMManager:
    """Picks a primary provider and falls back automatically on failure."""

    def __init__(self) -> None:
        settings = get_settings()
        ollama = OllamaProvider()
        groq = GroqProvider()

        if settings.llm_provider_primary == "ollama":
            self._providers: list[LLMProvider] = [ollama, groq]
        else:
            self._providers = [groq, ollama]

    async def generate_reply(self, conversation_history: list[dict[str, str]]) -> tuple[str, str]:
        """
        Generate a reply for the given conversation history.

        Returns (reply_text, provider_name_used) so the API layer can report
        which model produced the answer (shown in the frontend's "Model Used"
        indicator).
        """
        messages = [{"role": "system", "content": SYSTEM_PROMPT}, *conversation_history]

        last_error: Exception | None = None
        for provider in self._providers:
            try:
                reply = await provider.generate(messages)
                if reply:
                    return reply, provider.name
            except LLMError as exc:
                last_error = exc
                logger.warning("Provider '%s' failed, trying next fallback...", provider.name)
                continue

        raise LLMError(f"All LLM providers failed. Last error: {last_error}")


_manager_instance: LLMManager | None = None


def get_llm_manager() -> LLMManager:
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = LLMManager()
    return _manager_instance
