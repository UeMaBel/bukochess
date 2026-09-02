from unittest.mock import Mock, patch

import pytest

from app.ai.providers.openai import OpenAIProvider
from app.ai.settings import LLMSettings
from app.core.exceptions import LLMProviderException


class FakeTimeoutError(Exception):
    pass


class FakeRateLimitError(Exception):
    pass


class FakeLengthError(Exception):
    pass


class FakeConnectionError(Exception):
    pass


class FakeStatusError(Exception):
    status_code = 503


def _provider_with_error(error: Exception) -> OpenAIProvider:
    provider = OpenAIProvider.__new__(OpenAIProvider)
    provider.settings = LLMSettings(provider="openai", model="test-model")
    provider.client = Mock()
    provider.client.responses.parse.side_effect = error
    return provider


@pytest.mark.parametrize(
    ("exception_name", "error", "code", "retryable"),
    [
        ("APITimeoutError", FakeTimeoutError(), "timeout", True),
        ("RateLimitError", FakeRateLimitError(), "rate_limit", True),
        ("LengthFinishReasonError", FakeLengthError(), "max_output_tokens", True),
        ("APIConnectionError", FakeConnectionError(), "connection_error", True),
        ("APIStatusError", FakeStatusError(), "provider_error", True),
    ],
)
def test_openai_errors_are_classified(exception_name, error, code, retryable):
    provider = _provider_with_error(error)

    with patch(f"app.ai.providers.openai.{exception_name}", type(error)):
        with pytest.raises(LLMProviderException) as raised:
            provider.choose_move("test-fen", ["e2e4"])

    assert raised.value.code == code
    assert raised.value.retryable is retryable


def test_unexpected_openai_error_is_safe_and_not_retryable():
    provider = _provider_with_error(RuntimeError("secret provider details"))

    with pytest.raises(LLMProviderException) as raised:
        provider.choose_move("test-fen", ["e2e4"])

    assert raised.value.code == "unexpected_error"
    assert raised.value.message == "OpenAI could not choose a move."
    assert raised.value.retryable is False
    assert "secret provider details" not in raised.value.message
