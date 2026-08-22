"""
Conversation Manager

Orchestrates the AI conversation flow. This is the central component
that sits between the telephony/frontend and the LLM provider.

IMPORTANT: This module NEVER imports Ollama or Gemini directly.
It communicates ONLY through the LLMProvider interface via the factory.

Architecture:
    Customer → Telephony → STT → ConversationManager → LLM Provider → TTS → Customer
"""

import logging
import uuid
from dataclasses import dataclass, field

from app.services.ai.llm.base import LLMResponse
from app.services.ai.llm.factory import get_llm_provider, get_llm_provider_with_fallback

logger = logging.getLogger(__name__)


@dataclass
class ConversationSession:
    """Holds the state of a single conversation."""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: int | None = None
    system_prompt: str = "You are a helpful AI calling assistant. Be concise and professional."
    history: list[dict[str, str]] = field(default_factory=list)
    provider_name: str | None = None
    provider_config: dict | None = None
    is_active: bool = True
    call_id: str | None = None


class ConversationManager:
    """
    Manages AI conversations using the provider-agnostic LLM interface.

    The ConversationManager does NOT know or care which LLM provider is active.
    It simply calls:
        llm = get_llm_provider()
        response = await llm.generate(...)

    This makes the entire conversation system provider-independent.
    """

    def __init__(self):
        self._sessions: dict[str, ConversationSession] = {}

    def create_session(
        self,
        system_prompt: str | None = None,
        agent_id: int | None = None,
        provider_name: str | None = None,
        provider_config: dict | None = None,
    ) -> ConversationSession:
        """Create a new conversation session."""
        session = ConversationSession(
            system_prompt=system_prompt or ConversationSession.system_prompt,
            agent_id=agent_id,
            provider_name=provider_name,
            provider_config=provider_config,
        )
        self._sessions[session.session_id] = session
        logger.info("Created conversation session: %s", session.session_id)
        return session

    def get_session(self, session_id: str) -> ConversationSession | None:
        """Retrieve an existing session."""
        return self._sessions.get(session_id)

    async def process_message(
        self,
        session_id: str,
        user_message: str,
    ) -> LLMResponse:
        """
        Process a user message and return the AI response.

        This is the core method — it:
        1. Gets the appropriate LLM provider (via factory)
        2. Sends the message with full conversation history
        3. Records the exchange in session history
        4. Returns the standardized LLMResponse

        The calling engine code is IDENTICAL regardless of whether
        the response came from Ollama or Gemini.
        """
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        if not session.is_active:
            raise ValueError(f"Session is no longer active: {session_id}")

        # ── Generate response via the LLM factory ─────────────────────────
        # This is the KEY design: the conversation manager uses the factory,
        # not a specific provider. The provider can be swapped at runtime.
        response = await get_llm_provider_with_fallback(
            provider_name=session.provider_name,
            config_override=session.provider_config,
            system_prompt=session.system_prompt,
            conversation_history=session.history,
            user_message=user_message,
        )

        # ── Update conversation history ───────────────────────────────────
        session.history.append({"role": "user", "content": user_message})
        session.history.append({"role": "assistant", "content": response.text})

        logger.info(
            "Session %s: processed message (provider=%s, model=%s, latency=%dms)",
            session_id,
            response.provider,
            response.model,
            response.latency_ms,
        )

        return response

    def end_session(self, session_id: str) -> bool:
        """End a conversation session."""
        session = self._sessions.get(session_id)
        if not session:
            return False

        session.is_active = False
        logger.info(
            "Ended conversation session: %s (%d turns)",
            session_id,
            len(session.history) // 2,
        )
        return True

    def get_session_history(self, session_id: str) -> list[dict[str, str]]:
        """Get the conversation history for a session."""
        session = self._sessions.get(session_id)
        if not session:
            return []
        return session.history.copy()


# ── Module-level singleton ────────────────────────────────────────────────────
_conversation_manager: ConversationManager | None = None


def get_conversation_manager() -> ConversationManager:
    """Get the singleton ConversationManager instance."""
    global _conversation_manager
    if _conversation_manager is None:
        _conversation_manager = ConversationManager()
    return _conversation_manager
