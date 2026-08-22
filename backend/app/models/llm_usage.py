"""
LLM Usage Tracking Model

Records metadata for each LLM request for cost tracking and analytics.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class LLMUsage(Base):
    __tablename__ = "llm_usage"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # ── Provider info ─────────────────────────────────────────────────────
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    model: Mapped[str] = mapped_column(String(200), nullable=False)

    # ── Token usage ───────────────────────────────────────────────────────
    input_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # ── Cost & performance ────────────────────────────────────────────────
    estimated_cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # ── Context ───────────────────────────────────────────────────────────
    request_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    call_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    agent_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<LLMUsage provider={self.provider} model={self.model} "
            f"tokens={self.total_tokens}>"
        )
