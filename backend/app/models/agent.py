"""
Agent Model

Each agent can optionally override the global LLM provider/model.
If llm_provider is NULL, the agent uses the global LLM config.
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)

    # ── Per-agent LLM override (nullable = use global) ────────────────────
    llm_provider: Mapped[str | None] = mapped_column(String(50), nullable=True)
    llm_model: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # ── Agent behavior ────────────────────────────────────────────────────
    system_prompt: Mapped[str] = mapped_column(
        Text,
        default="You are a helpful AI calling assistant.",
        nullable=False,
    )
    language: Mapped[str] = mapped_column(String(50), default="English", nullable=False)
    voice: Mapped[str] = mapped_column(String(100), default="default", nullable=False)

    # ── Status ────────────────────────────────────────────────────────────
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        provider = self.llm_provider or "global"
        return f"<Agent name={self.name} provider={provider}>"
