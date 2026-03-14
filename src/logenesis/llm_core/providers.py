from __future__ import annotations

from abc import ABC, abstractmethod

from logenesis.schemas.models import ContextPacket


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, context: ContextPacket) -> str:
        raise NotImplementedError


class MockProvider(LLMProvider):
    def generate(self, prompt: str, context: ContextPacket) -> str:
        return f"[mock-answer topic={context.active_topic}] {prompt[:120]}"


class OpenAICompatibleProvider(LLMProvider):
    """Placeholder for OpenAI-compatible API providers.

    Intentionally left as a stub to keep local runnable behavior without vendor lock-in.
    """

    def __init__(self, base_url: str, api_key: str, model: str):
        self.base_url = base_url
        self.api_key = api_key
        self.model = model

    def generate(self, prompt: str, context: ContextPacket) -> str:
        return "[openai-compatible-placeholder] Configure HTTP client integration."
