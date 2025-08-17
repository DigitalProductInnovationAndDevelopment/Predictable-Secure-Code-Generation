"""AI-related ports for LLM and embeddings clients."""

from typing import Protocol, List, Dict, Any, Optional
from pydantic import BaseModel


class LLMResponse(BaseModel):
    """Response from an LLM."""

    content: str
    tokens_used: int
    model: str
    cost_estimate: Optional[float] = None
    finish_reason: Optional[str] = None


class LLMMessage(BaseModel):
    """Message for LLM conversation."""

    role: str  # "system", "user", "assistant"
    content: str


class LLMClient(Protocol):
    """Client for interacting with Large Language Models."""

    def complete(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate a completion from the LLM."""
        ...

    async def acomplete(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Async version of complete."""
        ...


class EmbeddingsClient(Protocol):
    """Client for generating embeddings."""

    def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for the given texts."""
        ...

    async def aembed(self, texts: List[str]) -> List[List[float]]:
        """Async version of embed."""
        ...
