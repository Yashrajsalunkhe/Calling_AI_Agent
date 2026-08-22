"""Pydantic schemas for LLM-related request/response models."""

from pydantic import BaseModel, Field


class LLMResponseSchema(BaseModel):
    """Standardized LLM response returned to the frontend."""
    text: str = ""
    intent: str = ""
    should_end_call: bool = False
    should_transfer: bool = False
    collected_information: dict = Field(default_factory=dict)
    usage: dict = Field(default_factory=dict)
    provider: str = ""
    model: str = ""
    latency_ms: int = 0


class ProviderStatusSchema(BaseModel):
    """Provider health check result."""
    provider: str = ""
    status: str = "unknown"
    model: str = ""
    message: str = ""
    latency_ms: int = 0


class ConversationStartRequest(BaseModel):
    """Request to start a new conversation."""
    system_prompt: str | None = None
    agent_id: int | None = None
    provider_name: str | None = None


class ConversationStartResponse(BaseModel):
    """Response after starting a conversation."""
    session_id: str
    message: str = "Conversation started"


class ConversationMessageRequest(BaseModel):
    """Send a message in an existing conversation."""
    message: str


class ConversationEndResponse(BaseModel):
    """Response after ending a conversation."""
    session_id: str
    message: str = "Conversation ended"
    total_turns: int = 0
