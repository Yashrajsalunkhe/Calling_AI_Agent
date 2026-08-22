"""
Conversation Router (Mock Call)

Provides endpoints for testing the AI conversation system.
The conversation flows through the ConversationManager → LLM Factory → Provider,
which is the exact same path that real telephony calls will use.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.agent import Agent
from app.models.llm_usage import LLMUsage
from app.schemas import (
    ConversationEndResponse,
    ConversationMessageRequest,
    ConversationStartRequest,
    ConversationStartResponse,
    LLMResponseSchema,
)
from app.services.ai.conversation import get_conversation_manager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/conversation", tags=["conversation"])


@router.post("/start", response_model=ConversationStartResponse)
async def start_conversation(
    req: ConversationStartRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Start a new mock conversation.

    If agent_id is provided, uses the agent's LLM provider/model and system prompt.
    Otherwise, uses the global LLM configuration.
    """
    manager = get_conversation_manager()

    system_prompt = req.system_prompt
    provider_name = req.provider_name
    provider_config = None

    # If agent_id is provided, load agent config
    if req.agent_id:
        result = await db.execute(
            select(Agent).where(Agent.id == req.agent_id)
        )
        agent = result.scalar_one_or_none()
        if agent:
            system_prompt = system_prompt or agent.system_prompt
            provider_name = provider_name or agent.llm_provider
            if agent.llm_model:
                provider_config = {"model": agent.llm_model}

    session = manager.create_session(
        system_prompt=system_prompt,
        agent_id=req.agent_id,
        provider_name=provider_name,
        provider_config=provider_config,
    )

    return ConversationStartResponse(
        session_id=session.session_id,
        message="Conversation started",
    )


@router.post("/{session_id}/message", response_model=LLMResponseSchema)
async def send_message(
    session_id: str,
    req: ConversationMessageRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Send a message in an existing conversation.

    The ConversationManager routes the message through the LLM factory.
    The same code path handles both Ollama and Gemini — the endpoint
    does not know or care which provider is active.
    """
    manager = get_conversation_manager()

    session = manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        response = await manager.process_message(session_id, req.message)

        # ── Record usage for tracking ─────────────────────────────────────
        usage_record = LLMUsage(
            provider=response.provider,
            model=response.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            total_tokens=response.usage.total_tokens,
            estimated_cost=0.0,  # TODO: Calculate based on provider pricing
            latency_ms=response.latency_ms,
            call_id=session.call_id,
            agent_id=session.agent_id,
        )
        db.add(usage_record)
        await db.flush()

        return LLMResponseSchema(**response.to_dict())

    except Exception as e:
        logger.error("Conversation error in session %s: %s", session_id, str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/end", response_model=ConversationEndResponse)
async def end_conversation(session_id: str):
    """End a conversation session."""
    manager = get_conversation_manager()

    session = manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    total_turns = len(session.history) // 2
    manager.end_session(session_id)

    return ConversationEndResponse(
        session_id=session_id,
        message="Conversation ended",
        total_turns=total_turns,
    )


@router.get("/{session_id}/history")
async def get_conversation_history(session_id: str):
    """Get the conversation history for a session."""
    manager = get_conversation_manager()
    history = manager.get_session_history(session_id)
    if not history and not manager.get_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session_id": session_id, "history": history}
