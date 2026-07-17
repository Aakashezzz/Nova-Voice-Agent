"""
Unit tests for LLMManager's fallback behaviour, using fake providers so
tests run without a live Ollama/Groq connection.
"""
import pytest

from app.core.exceptions import LLMError
from app.llm.base import LLMProvider
from app.llm.llm_manager import LLMManager


class _FakeFailingProvider(LLMProvider):
    name = "failing"

    async def generate(self, messages):
        raise LLMError("simulated failure")


class _FakeWorkingProvider(LLMProvider):
    name = "working"

    async def generate(self, messages):
        return "a working reply"


@pytest.mark.asyncio
async def test_falls_back_to_second_provider_on_failure():
    manager = LLMManager.__new__(LLMManager)  # bypass __init__ (avoids real client setup)
    manager._providers = [_FakeFailingProvider(), _FakeWorkingProvider()]

    reply, provider_used = await manager.generate_reply([{"role": "user", "content": "hi"}])

    assert reply == "a working reply"
    assert provider_used == "working"


@pytest.mark.asyncio
async def test_raises_when_all_providers_fail():
    manager = LLMManager.__new__(LLMManager)
    manager._providers = [_FakeFailingProvider(), _FakeFailingProvider()]

    with pytest.raises(LLMError):
        await manager.generate_reply([{"role": "user", "content": "hi"}])
