"""Abstract interface all LLM providers must implement."""
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """A chat-completion provider (e.g. Ollama, Groq)."""

    name: str

    @abstractmethod
    async def generate(self, messages: list[dict[str, str]]) -> str:
        """
        Generate a reply given a list of {"role", "content"} messages
        (OpenAI-style chat format). Should raise on failure so the
        LLMManager can fall back to the next provider.
        """
        raise NotImplementedError
