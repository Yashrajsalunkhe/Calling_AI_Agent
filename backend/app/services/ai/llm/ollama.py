"""
Ollama LLM Provider

Uses the official `ollama` Python package with AsyncClient.
Connects to a local/self-hosted Ollama instance.

Configuration:
    OLLAMA_BASE_URL=http://localhost:11434
    OLLAMA_MODEL=llama3.1
"""

import logging

import httpx
from ollama import AsyncClient

from app.services.ai.llm.base import LLMProvider, LLMResponse, ProviderStatus, UsageInfo

logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    """LLM provider for local Ollama models."""

    provider_name = "ollama"

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.1", timeout: int = 30):
        self.base_url = base_url
        self.model = model
        self.timeout = timeout
        self._client = AsyncClient(host=base_url)

    async def generate(
        self,
        system_prompt: str,
        conversation_history: list[dict[str, str]],
        user_message: str,
    ) -> LLMResponse:
        """Generate a response using Ollama's chat API."""
        start_ms = self._time_ms()

        # Build messages list
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        for msg in conversation_history:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", ""),
            })

        messages.append({"role": "user", "content": user_message})

        try:
            response = await self._client.chat(
                model=self.model,
                messages=messages,
            )

            latency_ms = int(self._time_ms() - start_ms)

            # Extract text
            raw_text = response.get("message", {}).get("content", "")

            # Extract token usage from Ollama response
            usage = UsageInfo(
                input_tokens=response.get("prompt_eval_count", 0) or 0,
                output_tokens=response.get("eval_count", 0) or 0,
                total_tokens=(
                    (response.get("prompt_eval_count", 0) or 0)
                    + (response.get("eval_count", 0) or 0)
                ),
            )

            return self._build_response(
                raw_text=raw_text,
                usage=usage,
                latency_ms=latency_ms,
                model=self.model,
            )

        except Exception as e:
            latency_ms = int(self._time_ms() - start_ms)
            logger.error("Ollama generation failed: %s", str(e))
            raise RuntimeError(f"Ollama provider error: {e}") from e

    async def health_check(self) -> ProviderStatus:
        """Check if Ollama server is reachable by listing models."""
        start_ms = self._time_ms()

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                resp.raise_for_status()

            latency_ms = int(self._time_ms() - start_ms)

            return ProviderStatus(
                provider=self.provider_name,
                status="connected",
                model=self.model,
                message="Ollama server is reachable",
                latency_ms=latency_ms,
            )

        except Exception as e:
            latency_ms = int(self._time_ms() - start_ms)
            return ProviderStatus(
                provider=self.provider_name,
                status="disconnected",
                model=self.model,
                message=f"Cannot reach Ollama: {e}",
                latency_ms=latency_ms,
            )
