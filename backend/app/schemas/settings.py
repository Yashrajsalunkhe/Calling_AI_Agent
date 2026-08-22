"""Pydantic schemas for Settings API."""

from pydantic import BaseModel, Field


class LLMSettingsResponse(BaseModel):
    """LLM configuration returned to the frontend.

    SECURITY: gemini_api_key is ALWAYS masked. The full key is never returned.
    """
    active_provider: str = "ollama"
    fallback_provider: str = ""
    fallback_enabled: bool = False

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"

    gemini_api_key_masked: str = ""  # e.g., "sk-...****xxxx"
    gemini_model: str = "gemini-2.0-flash"

    timeout_seconds: int = 30


class LLMSettingsUpdateRequest(BaseModel):
    """Request to update LLM settings."""
    active_provider: str | None = None
    fallback_provider: str | None = None
    fallback_enabled: bool | None = None

    ollama_base_url: str | None = None
    ollama_model: str | None = None

    gemini_api_key: str | None = None  # Plain text — encrypted before storage
    gemini_model: str | None = None

    timeout_seconds: int | None = None
