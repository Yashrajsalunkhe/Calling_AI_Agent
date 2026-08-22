"""
LLM Provider — Abstract Base Class

All LLM providers MUST inherit from this class and implement:
  - generate()    — produce a response from the LLM
  - health_check() — verify provider connectivity

The calling engine communicates ONLY through this interface.
It never imports Ollama or Gemini directly.
"""

import time
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class UsageInfo:
    """Token usage metadata from an LLM response."""
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


@dataclass
class LLMResponse:
    """
    Standardized response from any LLM provider.

    Regardless of whether the response came from Ollama or Gemini,
    the application receives this identical structure.
    """
    text: str = ""
    intent: str = ""
    should_end_call: bool = False
    should_transfer: bool = False
    collected_information: dict = field(default_factory=dict)
    usage: UsageInfo = field(default_factory=UsageInfo)
    provider: str = ""
    model: str = ""
    latency_ms: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "intent": self.intent,
            "should_end_call": self.should_end_call,
            "should_transfer": self.should_transfer,
            "collected_information": self.collected_information,
            "usage": {
                "input_tokens": self.usage.input_tokens,
                "output_tokens": self.usage.output_tokens,
                "total_tokens": self.usage.total_tokens,
            },
            "provider": self.provider,
            "model": self.model,
            "latency_ms": self.latency_ms,
        }


@dataclass
class ProviderStatus:
    """Health check result for a provider."""
    provider: str = ""
    status: str = "unknown"  # "connected", "configured", "disconnected", "error"
    model: str = ""
    message: str = ""
    latency_ms: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "status": self.status,
            "model": self.model,
            "message": self.message,
            "latency_ms": self.latency_ms,
        }


class LLMProvider(ABC):
    """
    Abstract base class for all LLM providers.

    Usage:
        llm = get_llm_provider()
        response = await llm.generate(
            system_prompt=system_prompt,
            conversation_history=history,
            user_message=user_message
        )

    The caller does not care whether the response came from Ollama or Gemini.
    """

    provider_name: str = "unknown"

    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        conversation_history: list[dict[str, str]],
        user_message: str,
    ) -> LLMResponse:
        """
        Generate a response from the LLM.

        Args:
            system_prompt: The system-level instruction for the AI agent.
            conversation_history: List of {"role": "user"|"assistant", "content": "..."}.
            user_message: The latest user message.

        Returns:
            LLMResponse with standardized fields.
        """
        ...

    @abstractmethod
    async def health_check(self) -> ProviderStatus:
        """
        Check if the provider is reachable and configured correctly.

        Returns:
            ProviderStatus with connection status.
        """
        ...

    def _build_response(
        self,
        raw_text: str,
        usage: UsageInfo,
        latency_ms: int,
        model: str,
    ) -> LLMResponse:
        """
        Build a standardized LLMResponse from raw provider output.

        Attempts to parse structured JSON from the LLM output.
        Falls back to plain text if JSON parsing fails.
        """
        response = LLMResponse(
            text=raw_text,
            usage=usage,
            provider=self.provider_name,
            model=model,
            latency_ms=latency_ms,
        )

        # Try to extract structured fields if the LLM returned JSON
        try:
            parsed = json.loads(raw_text)
            if isinstance(parsed, dict):
                response.text = parsed.get("text", raw_text)
                response.intent = parsed.get("intent", "")
                response.should_end_call = parsed.get("should_end_call", False)
                response.should_transfer = parsed.get("should_transfer", False)
                response.collected_information = parsed.get(
                    "collected_information", {}
                )
        except (json.JSONDecodeError, TypeError):
            # LLM returned plain text — that's fine
            pass

        return response

    @staticmethod
    def _time_ms() -> float:
        """Return current time in milliseconds for latency measurement."""
        return time.perf_counter() * 1000
