"""
LLM Provider Factory

Returns the appropriate LLM provider based on configuration.
The rest of the application simply does:

    llm = get_llm_provider()
    response = await llm.generate(...)

It does not care whether the response came from Ollama or Gemini.

Supports:
    - Global provider selection (from settings / DB config)
    - Per-agent provider override (via config_override)
    - Fallback provider (if primary fails)
"""

import logging

from app.config import get_settings
from app.services.ai.llm.base import LLMProvider, LLMResponse

logger = logging.getLogger(__name__)

# Registry of supported providers
_PROVIDER_REGISTRY: dict[str, type] = {}


def _ensure_registry():
    """Lazily populate the provider registry to avoid circular imports."""
    if _PROVIDER_REGISTRY:
        return

    from app.services.ai.llm.ollama import OllamaProvider
    from app.services.ai.llm.gemini import GeminiProvider

    _PROVIDER_REGISTRY["ollama"] = OllamaProvider
    _PROVIDER_REGISTRY["gemini"] = GeminiProvider


def get_llm_provider(
    provider_name: str | None = None,
    config_override: dict | None = None,
) -> LLMProvider:
    """
    Create and return an LLM provider instance.

    Args:
        provider_name: Which provider to use. Defaults to settings.LLM_PROVIDER.
        config_override: Optional dict to override default config
                         (used for per-agent LLM selection).

    Returns:
        An LLMProvider instance ready for generate() calls.

    Raises:
        ValueError: If the provider name is not supported.
    """
    _ensure_registry()
    settings = get_settings()

    name = (provider_name or settings.LLM_PROVIDER).lower().strip()

    if name not in _PROVIDER_REGISTRY:
        supported = ", ".join(_PROVIDER_REGISTRY.keys())
        raise ValueError(
            f"Unsupported LLM provider: '{name}'. Supported: {supported}"
        )

    # Build config kwargs for the provider
    override = config_override or {}

    if name == "ollama":
        kwargs = {
            "base_url": override.get("base_url", settings.OLLAMA_BASE_URL),
            "model": override.get("model", settings.OLLAMA_MODEL),
            "timeout": override.get("timeout", settings.LLM_TIMEOUT_SECONDS),
        }
    elif name == "gemini":
        kwargs = {
            "api_key": override.get("api_key", settings.GEMINI_API_KEY),
            "model": override.get("model", settings.GEMINI_MODEL),
            "timeout": override.get("timeout", settings.LLM_TIMEOUT_SECONDS),
        }
    else:
        kwargs = override

    return _PROVIDER_REGISTRY[name](**kwargs)


async def get_llm_provider_with_fallback(
    provider_name: str | None = None,
    config_override: dict | None = None,
    system_prompt: str = "",
    conversation_history: list[dict[str, str]] | None = None,
    user_message: str = "",
) -> LLMResponse:
    """
    Generate a response with automatic fallback on provider failure.

    1. Try the primary provider.
    2. If it fails AND fallback is enabled AND a fallback provider is configured,
       log the failure and retry with the fallback provider.
    3. If fallback also fails, raise the fallback error.

    This function NEVER silently switches — all failures are logged.
    """
    settings = get_settings()
    history = conversation_history or []

    # ── Try primary provider ──────────────────────────────────────────────
    primary_name = (provider_name or settings.LLM_PROVIDER).lower().strip()

    try:
        primary = get_llm_provider(primary_name, config_override)
        response = await primary.generate(system_prompt, history, user_message)
        return response

    except Exception as primary_error:
        logger.warning(
            "Primary LLM provider '%s' failed: %s",
            primary_name,
            str(primary_error),
        )

        # ── Check if fallback is available ────────────────────────────────
        fallback_name = settings.LLM_FALLBACK_PROVIDER.lower().strip()
        fallback_enabled = settings.LLM_FALLBACK_ENABLED

        if not fallback_enabled or not fallback_name:
            logger.error(
                "No fallback configured or fallback disabled. Raising error."
            )
            raise

        if fallback_name == primary_name:
            logger.error("Fallback is the same as primary. Raising error.")
            raise

        # ── Try fallback provider ─────────────────────────────────────────
        logger.info(
            "Attempting fallback to '%s' provider...",
            fallback_name,
        )

        try:
            fallback = get_llm_provider(fallback_name)
            response = await fallback.generate(system_prompt, history, user_message)

            logger.info(
                "Fallback to '%s' succeeded.",
                fallback_name,
            )
            return response

        except Exception as fallback_error:
            logger.error(
                "Fallback provider '%s' also failed: %s",
                fallback_name,
                str(fallback_error),
            )
            raise RuntimeError(
                f"Both primary ({primary_name}) and fallback ({fallback_name}) "
                f"providers failed."
            ) from fallback_error
