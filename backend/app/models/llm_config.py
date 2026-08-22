"""
Global LLM Configuration Model

Stores the runtime-switchable LLM provider settings.
Only one row exists (singleton config pattern).
The Gemini API key is stored encrypted.
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class LLMConfig(Base):
    __tablename__ = "llm_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)

    # ── Active provider ───────────────────────────────────────────────────
    active_provider: Mapped[str] = mapped_column(
        String(50), default="ollama", nullable=False
    )
    fallback_provider: Mapped[str] = mapped_column(
        String(50), default="", nullable=False
    )
    fallback_enabled: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # ── Ollama settings ───────────────────────────────────────────────────
    ollama_base_url: Mapped[str] = mapped_column(
        String(500), default="http://localhost:11434", nullable=False
    )
    ollama_model: Mapped[str] = mapped_column(
        String(200), default="llama3.1", nullable=False
    )

    # ── Gemini settings ───────────────────────────────────────────────────
    # Stored encrypted — never returned in plain text via API
    gemini_api_key_encrypted: Mapped[str] = mapped_column(
        Text, default="", nullable=False
    )
    gemini_model: Mapped[str] = mapped_column(
        String(200), default="gemini-2.0-flash", nullable=False
    )

    # ── General ───────────────────────────────────────────────────────────
    timeout_seconds: Mapped[int] = mapped_column(
        Integer, default=30, nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<LLMConfig provider={self.active_provider} "
            f"fallback={self.fallback_provider}>"
        )
