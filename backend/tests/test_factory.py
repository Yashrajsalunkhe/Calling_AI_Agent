"""Unit tests for the LLM provider factory and base classes."""

import pytest
from unittest.mock import patch
import sys
import os

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
    from app.services.ai.llm import factory
    factory._PROVIDER_REGISTRY.clear()
    yield
    factory._PROVIDER_REGISTRY.clear()


@patch("app.services.ai.llm.factory.get_settings", return_value=MockSettings())
def test_get_llm_provider_ollama(mock_settings):
    from app.services.ai.llm.factory import get_llm_provider
    from app.services.ai.llm.ollama import OllamaProvider
    provider = get_llm_provider("ollama")
    assert isinstance(provider, OllamaProvider)
    assert provider.provider_name == "ollama"


@patch("app.services.ai.llm.factory.get_settings", return_value=MockSettings())
def test_get_llm_provider_gemini(mock_settings):
    from app.services.ai.llm.factory import get_llm_provider
    from app.services.ai.llm.gemini import GeminiProvider
    provider = get_llm_provider("gemini")
    assert isinstance(provider, GeminiProvider)
    assert provider.provider_name == "gemini"


@patch("app.services.ai.llm.factory.get_settings", return_value=MockSettings())
def test_get_llm_provider_default_from_settings(mock_settings):
    from app.services.ai.llm.factory import get_llm_provider
    from app.services.ai.llm.ollama import OllamaProvider
    provider = get_llm_provider()
    assert isinstance(provider, OllamaProvider)


@patch("app.services.ai.llm.factory.get_settings", return_value=MockSettings())
def test_get_llm_provider_unsupported_raises(mock_settings):
    from app.services.ai.llm.factory import get_llm_provider
    with pytest.raises(ValueError, match="Unsupported LLM provider"):
        get_llm_provider("openai")


@patch("app.services.ai.llm.factory.get_settings", return_value=MockSettings())
def test_config_override(mock_settings):
    from app.services.ai.llm.factory import get_llm_provider
    provider = get_llm_provider("ollama", config_override={"model": "phi4"})
    assert provider.model == "phi4"


def test_llm_response_to_dict():
    from app.services.ai.llm.base import LLMResponse, UsageInfo
    r = LLMResponse(
        text="Hi", intent="greet", provider="ollama", model="llama3.1",
        latency_ms=100, usage=UsageInfo(10, 5, 15),
    )
    d = r.to_dict()
    assert d["text"] == "Hi"
    assert d["provider"] == "ollama"
    assert d["usage"]["total_tokens"] == 15
    assert d["should_end_call"] is False


def test_provider_status_to_dict():
    from app.services.ai.llm.base import ProviderStatus
    s = ProviderStatus(provider="gemini", status="connected", model="m", message="ok", latency_ms=50)
    d = s.to_dict()
    assert d["status"] == "connected"


@pytest.mark.asyncio
async def test_gemini_health_check_awaits_model_pager():
    from types import SimpleNamespace
    from app.services.ai.llm.gemini import GeminiProvider

    class ModelPager:
        def __aiter__(self):
            return self._models()

        async def _models(self):
            for name in ("models/one", "models/two"):
                yield SimpleNamespace(name=name)

    class Models:
        async def list(self):
            return ModelPager()

    provider = GeminiProvider.__new__(GeminiProvider)
    provider.model = "gemini-2.0-flash"
    provider._client = SimpleNamespace(aio=SimpleNamespace(models=Models()))

    status = await provider.health_check()

    assert status.status == "connected"
    assert status.message == "Gemini API connected (2 models available)"


def test_build_response_plain_text():
    from app.services.ai.llm.base import LLMProvider, UsageInfo
    # Can't instantiate abstract class directly, but _build_response is concrete
    # Use a minimal subclass
    class TestProvider(LLMProvider):
        provider_name = "test"
        async def generate(self, *a, **kw): pass
        async def health_check(self): pass

    p = TestProvider()
    r = p._build_response("Hello world", UsageInfo(10, 5, 15), 200, "test-model")
    assert r.text == "Hello world"
    assert r.intent == ""  # plain text, no JSON


def test_build_response_json_structured():
    from app.services.ai.llm.base import LLMProvider, UsageInfo
    import json

    class TestProvider(LLMProvider):
        provider_name = "test"
        async def generate(self, *a, **kw): pass
        async def health_check(self): pass

    p = TestProvider()
    structured = json.dumps({
        "text": "How can I help?",
        "intent": "greeting",
        "should_end_call": False,
        "collected_information": {"name": "John"},
    })
    r = p._build_response(structured, UsageInfo(10, 5, 15), 200, "test-model")
    assert r.text == "How can I help?"
    assert r.intent == "greeting"
    assert r.collected_information == {"name": "John"}
