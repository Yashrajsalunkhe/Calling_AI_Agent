"""
Provider Status & Test Connection Router

Endpoints for checking provider connectivity and testing connections
without exposing credentials.
"""

import logging

from fastapi import APIRouter

from app.config import get_settings
from app.services.ai.llm.factory import get_llm_provider

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/providers", tags=["providers"])


@router.get("/status")
async def get_all_provider_status():
    """
    Get the status of all configured providers.

    Returns connection status for each provider without exposing credentials.
    """
    settings = get_settings()
    statuses = []

    # ── Ollama status ─────────────────────────────────────────────────────
    try:
        ollama = get_llm_provider("ollama")
        ollama_status = await ollama.health_check()
        statuses.append(ollama_status.to_dict())
    except Exception as e:
        statuses.append({
            "provider": "ollama",
            "status": "error",
            "model": settings.OLLAMA_MODEL,
            "message": str(e),
            "latency_ms": 0,
        })

    # ── Gemini status ─────────────────────────────────────────────────────
    if settings.GEMINI_API_KEY:
        try:
            gemini = get_llm_provider("gemini")
            gemini_status = await gemini.health_check()
            statuses.append(gemini_status.to_dict())
        except Exception as e:
            error_msg = str(e)
            if "api_key" in error_msg.lower():
                error_msg = "Configuration error (credentials redacted)"
            statuses.append({
                "provider": "gemini",
                "status": "error",
                "model": settings.GEMINI_MODEL,
                "message": error_msg,
                "latency_ms": 0,
            })
    else:
        statuses.append({
            "provider": "gemini",
            "status": "not_configured",
            "model": settings.GEMINI_MODEL,
            "message": "API key not set",
            "latency_ms": 0,
        })

    return {
        "active_provider": settings.LLM_PROVIDER,
        "providers": statuses,
    }


@router.post("/{provider_name}/test")
async def test_provider_connection(provider_name: str):
    """
    Test connection to a specific provider.

    Tests the provider without exposing credentials in the response.
    """
    try:
        provider = get_llm_provider(provider_name)
        status = await provider.health_check()
        return status.to_dict()
    except ValueError as e:
        return {
            "provider": provider_name,
            "status": "error",
            "model": "",
            "message": str(e),
            "latency_ms": 0,
        }
    except Exception as e:
        error_msg = str(e)
        if "api_key" in error_msg.lower():
            error_msg = "Configuration error (credentials redacted)"
        return {
            "provider": provider_name,
            "status": "error",
            "model": "",
            "message": error_msg,
            "latency_ms": 0,
        }
