from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from app.ai.models import LLMDecision, LLMDecisionMetadata, LLMProviderMetadata, LLMProviderResult
from app.chess.engines.llm_engine import LLMEngine
from app.core.exceptions import LLMProviderException
from app.main import app


client = TestClient(app)
START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
LLM_METADATA = {
    "provider": "openai",
    "model": "test-model",
}


def _post_llm_move():
    return client.post(
        "/api/v1/engine/move",
        json={"fen": START_FEN, "engine": "llm", "metadata": LLM_METADATA},
    )


@pytest.mark.parametrize(
    ("code", "message", "retryable"),
    [
        ("timeout", "The OpenAI request timed out.", True),
        ("rate_limit", "OpenAI rate limit reached.", True),
        ("max_output_tokens", "OpenAI reached the token limit.", True),
        ("provider_error", "OpenAI API error (500).", True),
    ],
)
def test_llm_provider_error_is_returned_as_metadata(code, message, retryable):
    provider = Mock()
    provider.choose_move.side_effect = LLMProviderException(
        code, message, retryable=retryable
    )

    with patch.object(LLMEngine, "_create_provider", return_value=provider):
        response = _post_llm_move()

    assert response.status_code == 200
    body = response.json()
    assert body["fen"] == START_FEN
    assert body["move"] is None
    assert body["status"] == "ok"
    assert body["engine"] == "LLM"
    assert body["played_color"] == "w"
    assert body["metadata"]["error"] == {
        "code": code,
        "message": message,
        "retryable": retryable,
    }


def test_unexpected_llm_provider_error_is_safe():
    provider = Mock()
    provider.choose_move.side_effect = RuntimeError("secret provider details")

    with patch.object(LLMEngine, "_create_provider", return_value=provider):
        response = _post_llm_move()

    error = response.json()["metadata"]["error"]
    assert error == {
        "code": "unexpected_error",
        "message": "The openai provider could not choose a move.",
        "retryable": False,
    }
    assert "secret provider details" not in response.text


def test_illegal_llm_move_is_returned_as_metadata():
    provider = Mock()
    provider.choose_move.return_value = LLMProviderResult(
        decision=LLMDecision(
            move="e2e5",
            metadata=LLMDecisionMetadata(),
        ),
        metadata=LLMProviderMetadata(),
    )

    with patch.object(LLMEngine, "_create_provider", return_value=provider):
        response = _post_llm_move()

    assert response.status_code == 200
    assert response.json()["move"] is None
    assert response.json()["metadata"]["error"]["code"] == "illegal_move"


def test_successful_llm_move_still_advances_the_position():
    provider = Mock()
    provider.choose_move.return_value = LLMProviderResult(
        decision=LLMDecision(
            move="e2e4",
            metadata=LLMDecisionMetadata(),
        ),
        metadata=LLMProviderMetadata(),
    )

    with patch.object(LLMEngine, "_create_provider", return_value=provider):
        response = _post_llm_move()

    assert response.status_code == 200
    assert response.json()["move"] == "e2e4"
    assert response.json()["fen"] != START_FEN
    assert "error" not in response.json()["metadata"]
