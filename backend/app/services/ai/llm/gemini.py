"""
Google Gemini LLM Provider

Uses the unified `google-genai` SDK with async client.
All API calls are made from the backend — never from the frontend.

Configuration:
    GEMINI_API_KEY=your-key-here
    GEMINI_MODEL=gemini-2.0-flash

Security:
    - API key is never logged
    - API key is never sent to the frontend
    - API key is never exposed in error messages
"""

import logging

from google import genai
from google.genai import types

from app.services.ai.llm.base import LLMProvider, LLMResponse, ProviderStatus, UsageInfo

logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    """LLM provider for Google Gemini API."""

    provider_name = "gemini"

    def __init__(self, api_key: str = "", model: str = "gemini-2.0-flash", timeout: int = 30):
        if not api_key:
            raise ValueError("Gemini API key is required")

        self.model = model
        self.timeout = timeout
        # Initialize the unified google-genai client
        self._client = genai.Client(api_key=api_key)

    async def generate(
        self,
        system_prompt: str,
        conversation_history: list[dict[str, str]],
        user_message: str,
    ) -> LLMResponse:
        """Generate a response using Gemini's async API."""
        start_ms = self._time_ms()

        try:
            # Build contents list for Gemini
            contents = []

            for msg in conversation_history:
                role = msg.get("role", "user")
                # Gemini uses "user" and "model" roles (not "assistant")
                if role == "assistant":
                    role = "model"
                contents.append(
                    types.Content(
                        role=role,
                        parts=[types.Part(text=msg.get("content", ""))],
                    )
                )

            # Add the current user message
            contents.append(
                types.Content(
                    role="user",
                    parts=[types.Part(text=user_message)],
                )
            )

            # Configure generation with system instruction
            config = types.GenerateContentConfig(
                system_instruction=system_prompt if system_prompt else None,
                temperature=0.7,
            )

            # Use async client
            response = await self._client.aio.models.generate_content(
                model=self.model,
                contents=contents,
                config=config,
            )

            latency_ms = int(self._time_ms() - start_ms)

            # Extract text
            raw_text = response.text or ""

            # Extract token usage from Gemini response metadata
            usage_meta = response.usage_metadata
            usage = UsageInfo(
                input_tokens=getattr(usage_meta, "prompt_token_count", 0) or 0,
                output_tokens=getattr(usage_meta, "candidates_token_count", 0) or 0,
                total_tokens=getattr(usage_meta, "total_token_count", 0) or 0,
            )

            return self._build_response(
                raw_text=raw_text,
                usage=usage,
                latency_ms=latency_ms,
                model=self.model,
            )

        except Exception as e:
            latency_ms = int(self._time_ms() - start_ms)
            # NEVER log the API key
            error_msg = str(e)
            if "api_key" in error_msg.lower() or "apikey" in error_msg.lower():
                error_msg = "Gemini authentication error (credentials redacted)"
            logger.error("Gemini generation failed: %s", error_msg)
            raise RuntimeError(f"Gemini provider error: {error_msg}") from e

    async def health_check(self) -> ProviderStatus:
        """Verify Gemini API key and connectivity by listing models."""
        start_ms = self._time_ms()

        try:
            # Use the async client to list models as a connectivity test
            models = []
            model_pager = await self._client.aio.models.list()
            async for model in model_pager:
                models.append(model.name)
                if len(models) >= 3:
                    break

            latency_ms = int(self._time_ms() - start_ms)

            return ProviderStatus(
                provider=self.provider_name,
                status="connected",
                model=self.model,
                message=f"Gemini API connected ({len(models)} models available)",
                latency_ms=latency_ms,
            )

        except Exception as e:
            latency_ms = int(self._time_ms() - start_ms)
            error_msg = str(e)
            # Sanitize — never expose the API key in status messages
            if "api_key" in error_msg.lower() or "apikey" in error_msg.lower():
                error_msg = "Authentication error (credentials redacted)"

            return ProviderStatus(
                provider=self.provider_name,
                status="error",
                model=self.model,
                message=f"Gemini error: {error_msg}",
                latency_ms=latency_ms,
            )
