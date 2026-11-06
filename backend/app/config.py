"""
AI Calling Agent — Application Configuration

Loads environment variables via pydantic-settings.
All LLM provider config, database URL, and app secrets are managed here.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── LLM Provider ─────────────────────────────────────────────────────
    LLM_PROVIDER: str = "ollama"
    LLM_FALLBACK_PROVIDER: str = ""
    LLM_FALLBACK_ENABLED: bool = False
    LLM_TIMEOUT_SECONDS: int = 30

    # ── Ollama ────────────────────────────────────────────────────────────
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1"

    # ── Gemini ────────────────────────────────────────────────────────────
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # ── Text-to-speech ────────────────────────────────────────────────────
    VEXYL_TTS_URL: str = ""
    VEXYL_TTS_API_KEY: str = ""
    VEXYL_TTS_TIMEOUT_SECONDS: int = 30

    # ── Application ───────────────────────────────────────────────────────
    APP_SECRET_KEY: str = "change-this-to-a-random-secret-key"
    DATABASE_URL: str = "sqlite+aiosqlite:///./calling_agent.db"
    CORS_ORIGINS: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


@lru_cache
def get_settings() -> Settings:
    """Cached singleton for application settings."""
    return Settings()
