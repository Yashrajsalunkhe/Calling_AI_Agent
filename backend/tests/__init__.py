"""Unit tests for the LLM provider factory."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

# We need to mock settings before importing factory
import sys
import os

# Add the app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class MockSettings:
    LLM_PROVIDER = "ollama"
    LLM_FALLBACK_PROVIDER = "gemini"
    LLM_FALLBACK_ENABLED = True
    LLM_TIMEOUT_SECONDS = 30
    OLLAMA_BASE_URL = "http://localhost:11434"
    OLLAMA_MODEL = "llama3.1"
    GEMINI_API_KEY = "test-key-123"
    GEMINI_MODEL = "gemini-2.0-flash"


@pytest.fixture(autouse=True)
def reset_registry():
    """Reset the provider registry between tests."""
    from app.services.ai.llm import factory
    factory._PROVIDER_REGISTRY.clear()
    yield
    factory._PROVIDER_REGISTRY.clear()


@patch("app.services.ai.llm.factory.get_settings", return_value=MockSettings())
def test_get_llm_provider_ollama(mock_settings):
    """Test factory returns OllamaProvider when ollama is selected."""
    from app.services.ai.llm.factory import get_llm_provider
    from app.services.ai.llm.ollama import OllamaProvider

    provider = get_llm_provider("ollama")
    assert isinstance(provider, OllamaProvider)
    assert provider.provider_name == "ollama"
    assert provider.model == "llama3.1"


@patch("app.services.ai.llm.factory.get_settings", return_value=MockSettings())
def test_get_llm_provider_gemini(mock_settings):
    """Test factory returns GeminiProvider when gemini is selected."""
    from app.services.ai.llm.factory import get_llm_provider
    from app.services.ai.llm.gemini import GeminiProvider

    provider = get_llm_provider("gemini")
    assert isinstance(provider, GeminiProvider)
    assert provider.provider_name == "gemini"
    assert provider.model == "gemini-2.0-flash"


@patch("app.services.ai.llm.factory.get_settings", return_value=MockSettings())
def test_get_llm_provider_default(mock_settings):
    """Test factory uses settings.LLM_PROVIDER when no name is given."""
    from app.services.ai.llm.factory import get_llm_provider
    from app.services.ai.llm.ollama import OllamaProvider

    provider = get_llm_provider()  # No provider_name
    assert isinstance(provider, OllamaProvider)


@patch("app.services.ai.llm.factory.get_settings", return_value=MockSettings())
def test_get_llm_provider_unsupported(mock_settings):
    """Test factory raises ValueError for unsupported providers."""
    from app.services.ai.llm.factory import get_llm_provider

    with pytest.raises(ValueError, match="Unsupported LLM provider"):
        get_llm_provider("openai")


@patch("app.services.ai.llm.factory.get_settings", return_value=MockSettings())
def test_get_llm_provider_with_config_override(mock_settings):
    """Test factory applies config overrides (for per-agent config)."""
    from app.services.ai.llm.factory import get_llm_provider

    provider = get_llm_provider("ollama", config_override={"model": "custom-model"})
    assert provider.model == "custom-model"


def test_llm_response_to_dict():
    """Test LLMResponse serialization."""
    from app.services.ai.llm.base import LLMResponse, UsageInfo

    response = LLMResponse(
        text="Hello",
        intent="greeting",
        provider="ollama",
        model="llama3.1",
        latency_ms=100,
        usage=UsageInfo(input_tokens=10, output_tokens=5, total_tokens=15),
    )
    d = response.to_dict()

    assert d["text"] == "Hello"
    assert d["intent"] == "greeting"
    assert d["provider"] == "ollama"
    assert d["model"] == "llama3.1"
    assert d["latency_ms"] == 100
    assert d["usage"]["total_tokens"] == 15
    assert d["should_end_call"] is False


def test_provider_status_to_dict():
    """Test ProviderStatus serialization."""
    from app.services.ai.llm.base import ProviderStatus

    status = ProviderStatus(
        provider="gemini",
        status="connected",
        model="gemini-2.0-flash",
        message="OK",
        latency_ms=50,
    )
    d = status.to_dict()

    assert d["provider"] == "gemini"
    assert d["status"] == "connected"
    assert d["latency_ms"] == 50
