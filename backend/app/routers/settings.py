"""
Settings API Router

Manages the global LLM configuration.
Supports runtime provider switching without rebuilding the application.

Security:
    - API key is encrypted before storage
    - API key is NEVER returned in plain text
    - Only a masked version is sent to the frontend
"""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.llm_config import LLMConfig
from app.schemas.settings import LLMSettingsResponse, LLMSettingsUpdateRequest
from app.security import decrypt_api_key, encrypt_api_key, mask_api_key

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/settings", tags=["settings"])


async def _get_or_create_config(db: AsyncSession) -> LLMConfig:
    """Get the singleton LLM config, creating it if it doesn't exist."""
    result = await db.execute(select(LLMConfig).where(LLMConfig.id == 1))
    config = result.scalar_one_or_none()
    if not config:
        config = LLMConfig(id=1)
        db.add(config)
        await db.flush()
    return config


@router.get("/llm", response_model=LLMSettingsResponse)
async def get_llm_settings(db: AsyncSession = Depends(get_db)):
    """
    Get current LLM settings.

    The Gemini API key is returned MASKED — never in plain text.
    """
    config = await _get_or_create_config(db)

    # Decrypt the key only to mask it — never return the full key
    decrypted_key = decrypt_api_key(config.gemini_api_key_encrypted)
    masked_key = mask_api_key(decrypted_key)

    return LLMSettingsResponse(
        active_provider=config.active_provider,
        fallback_provider=config.fallback_provider,
        fallback_enabled=config.fallback_enabled,
        ollama_base_url=config.ollama_base_url,
        ollama_model=config.ollama_model,
        gemini_api_key_masked=masked_key,
        gemini_model=config.gemini_model,
        timeout_seconds=config.timeout_seconds,
    )


@router.put("/llm", response_model=LLMSettingsResponse)
async def update_llm_settings(
    req: LLMSettingsUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Update LLM settings.

    When the provider is changed, future calls use the new provider
    WITHOUT requiring an application restart.

    The Gemini API key is encrypted before storage.
    """
    config = await _get_or_create_config(db)

    # Update only the fields that were provided
    if req.active_provider is not None:
        config.active_provider = req.active_provider
    if req.fallback_provider is not None:
        config.fallback_provider = req.fallback_provider
    if req.fallback_enabled is not None:
        config.fallback_enabled = req.fallback_enabled
    if req.ollama_base_url is not None:
        config.ollama_base_url = req.ollama_base_url
    if req.ollama_model is not None:
        config.ollama_model = req.ollama_model
    if req.gemini_api_key is not None and req.gemini_api_key.strip():
        # Encrypt before storage — never store plain text
        config.gemini_api_key_encrypted = encrypt_api_key(req.gemini_api_key)
    if req.gemini_model is not None:
        config.gemini_model = req.gemini_model
    if req.timeout_seconds is not None:
        config.timeout_seconds = req.timeout_seconds

    await db.flush()

    logger.info(
        "LLM settings updated: provider=%s, fallback=%s",
        config.active_provider,
        config.fallback_provider,
    )

    # Return the updated settings with masked key
    decrypted_key = decrypt_api_key(config.gemini_api_key_encrypted)
    masked_key = mask_api_key(decrypted_key)

    return LLMSettingsResponse(
        active_provider=config.active_provider,
        fallback_provider=config.fallback_provider,
        fallback_enabled=config.fallback_enabled,
        ollama_base_url=config.ollama_base_url,
        ollama_model=config.ollama_model,
        gemini_api_key_masked=masked_key,
        gemini_model=config.gemini_model,
        timeout_seconds=config.timeout_seconds,
    )
