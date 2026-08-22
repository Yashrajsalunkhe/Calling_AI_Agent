"""Pydantic schemas for Agent API."""

from pydantic import BaseModel
from datetime import datetime


class AgentCreateRequest(BaseModel):
    """Request to create a new agent."""
    name: str
    description: str = ""
    llm_provider: str | None = None
    llm_model: str | None = None
    system_prompt: str = "You are a helpful AI calling assistant."
    language: str = "English"
    voice: str = "default"


class AgentUpdateRequest(BaseModel):
    """Request to update an agent."""
    name: str | None = None
    description: str | None = None
    llm_provider: str | None = None
    llm_model: str | None = None
    system_prompt: str | None = None
    language: str | None = None
    voice: str | None = None
    is_active: bool | None = None


class AgentResponse(BaseModel):
    """Agent detail response."""
    id: int
    name: str
    description: str = ""
    llm_provider: str | None = None
    llm_model: str | None = None
    system_prompt: str = ""
    language: str = "English"
    voice: str = "default"
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
