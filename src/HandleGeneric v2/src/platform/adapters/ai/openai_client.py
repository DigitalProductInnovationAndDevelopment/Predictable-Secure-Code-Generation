"""OpenAI client adapter supporting both OpenAI and Azure OpenAI."""

import openai
from typing import List, Optional, Any
from platform.ports.ai import LLMClient, LLMResponse, LLMMessage
from platform.kernel.logging import get_logger

logger = get_logger(__name__)


class OpenAIClient:
    """OpenAI client adapter."""

    def __init__(
        self,
        api_key: str,
        is_azure: bool = False,
        azure_endpoint: Optional[str] = None,
        api_version: Optional[str] = None,
        azure_deployment: Optional[str] = None,
    ):
        self.is_azure = is_azure
        self.api_key = api_key

        if is_azure:
            self.client = openai.AzureOpenAI(
                api_key=api_key,
                azure_endpoint=azure_endpoint,
                api_version=api_version or "2023-12-01-preview",
            )
            self.deployment = azure_deployment
        else:
            self.client = openai.OpenAI(api_key=api_key)
            self.deployment = None

    def complete(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate completion from OpenAI."""
        try:
            # Convert LLMMessage to dict format
            message_dicts = [{"role": msg.role, "content": msg.content} for msg in messages]

            # Use deployment name for Azure, model name for OpenAI
            model_param = self.deployment if self.is_azure else (model or "gpt-4")

            response = self.client.chat.completions.create(
                model=model_param,
                messages=message_dicts,
                temperature=temperature or 0.0,
                max_tokens=max_tokens or 4000,
                **kwargs,
            )

            logger.info(
                "OpenAI completion successful",
                model=model_param,
                tokens_used=response.usage.total_tokens,
                finish_reason=response.choices[0].finish_reason,
            )

            return LLMResponse(
                content=response.choices[0].message.content,
                tokens_used=response.usage.total_tokens,
                model=model_param,
                finish_reason=response.choices[0].finish_reason,
                cost_estimate=self._estimate_cost(response.usage.total_tokens, model_param),
            )

        except Exception as e:
            logger.error("OpenAI completion failed", error=str(e))
            raise

    async def acomplete(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Async completion - for now just call sync version."""
        return self.complete(messages, model, temperature, max_tokens, **kwargs)

    def _estimate_cost(self, tokens: int, model: str) -> float:
        """Estimate cost in USD based on token usage."""
        # Rough cost estimates per 1K tokens (as of 2024)
        costs = {
            "gpt-4": 0.03,
            "gpt-4-32k": 0.06,
            "gpt-3.5-turbo": 0.002,
        }

        base_cost = costs.get(model, 0.03)  # Default to GPT-4 pricing
        return (tokens / 1000) * base_cost
