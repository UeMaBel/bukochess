from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.ai.models import (
    LLMDecision,
    LLMDecisionMetadata,
    LLMProviderMetadata,
    LLMProviderResult,
)
from app.chess.board_mailbox import BoardMailbox
from app.chess.engines.llm_engine import LLMEngine
from app.chess.move_mailbox import MoveMailBoxGenerator
from app.core.config import settings as app_settings
from app.core.exceptions import LLMProviderException

ENGINE_MOVE_URL = "/api/v1/engine/move"
LLM_METADATA = {
    "provider": "openai",
    "model": "test-model",
    "reasoningEffort": "low",
    "temperature": 0.2,
    "maxOutputTokens": 128,
    "explanation": True,
}


@pytest.fixture(autouse=True)
def configure_dummy_openai_key(monkeypatch: pytest.MonkeyPatch):
    """Allow mocked provider tests to run without a real OpenAI credential."""
    monkeypatch.setattr(app_settings, "openai_api_key", SecretStr("test-key"))


def _request_llm_move(client: TestClient, fen: str):
    return client.post(
        ENGINE_MOVE_URL,
        json={"fen": fen, "engine": "llm", "metadata": LLM_METADATA},
    )


def _provider_result(move: str) -> LLMProviderResult:
    return LLMProviderResult(
        decision=LLMDecision(
            move=move,
            metadata=LLMDecisionMetadata(
                explanation="A sensible developing move.",
                confidence=0.8,
            ),
        ),
        metadata=LLMProviderMetadata(
            input_tokens=20,
            output_tokens=8,
            latency_ms=15,
        ),
    )


def test_llm_success_response_contract_for_both_colors(
    client: TestClient,
    engine_position: tuple[str, str],
):
    color, fen = engine_position
    chosen_move = "e2e4" if color == "w" else "e7e5"
    provider = Mock()
    provider.choose_move.return_value = _provider_result(chosen_move)

    with patch.object(LLMEngine, "_create_provider", return_value=provider):
        response = _request_llm_move(client, fen)

    assert response.status_code == 200
    body = response.json()
    assert body["move"] == chosen_move
    assert body["engine"] == "LLM"
    assert body["played_color"] == color
    assert body["status"] == "ok"
    assert "error" not in body["metadata"]
    assert body["metadata"] == {
        "provider": "openai",
        "model": "test-model",
        "reasoning_effort": "low",
        "temperature": 0.2,
        "max_output_tokens": 128,
        "explanation": "A sensible developing move.",
        "confidence": 0.8,
        "input_tokens": 20,
        "output_tokens": 8,
        "latency_ms": 15,
    }

    board = BoardMailbox()
    board.from_fen(fen)
    MoveMailBoxGenerator(board).apply_uci(chosen_move)
    assert body["fen"] == board.to_fen()

    provider.choose_move.assert_called_once()
    provider_fen, legal_moves = provider.choose_move.call_args.args
    assert provider_fen == fen
    assert chosen_move in legal_moves


@pytest.mark.parametrize(
    ("code", "message", "retryable"),
    [
        ("timeout", "The OpenAI request timed out.", True),
        ("rate_limit", "OpenAI rate limit reached.", True),
        ("max_output_tokens", "OpenAI reached the token limit.", True),
        ("provider_error", "OpenAI API error (500).", True),
    ],
)
def test_llm_provider_error_is_returned_as_metadata_for_both_colors(
    client: TestClient,
    engine_position: tuple[str, str],
    code: str,
    message: str,
    retryable: bool,
):
    color, fen = engine_position
    provider = Mock()
    provider.choose_move.side_effect = LLMProviderException(
        code, message, retryable=retryable
    )

    with patch.object(LLMEngine, "_create_provider", return_value=provider):
        response = _request_llm_move(client, fen)

    assert response.status_code == 200
    body = response.json()
    assert body["fen"] == fen
    assert body["move"] is None
    assert body["status"] == "ok"
    assert body["engine"] == "LLM"
    assert body["played_color"] == color
    assert body["metadata"]["error"] == {
        "code": code,
        "message": message,
        "retryable": retryable,
    }


def test_unexpected_llm_provider_error_is_safe_for_both_colors(
    client: TestClient,
    engine_position: tuple[str, str],
):
    _, fen = engine_position
    provider = Mock()
    provider.choose_move.side_effect = RuntimeError("secret provider details")

    with patch.object(LLMEngine, "_create_provider", return_value=provider):
        response = _request_llm_move(client, fen)

    assert response.status_code == 200
    assert response.json()["metadata"]["error"] == {
        "code": "unexpected_error",
        "message": "The openai provider could not choose a move.",
        "retryable": False,
    }
    assert "secret provider details" not in response.text


def test_missing_openai_key_is_returned_without_constructing_provider_for_both_colors(
    client: TestClient,
    engine_position: tuple[str, str],
    monkeypatch: pytest.MonkeyPatch,
):
    color, fen = engine_position
    monkeypatch.setattr(app_settings, "openai_api_key", SecretStr(""))

    with patch.object(LLMEngine, "_create_provider") as create_provider:
        response = _request_llm_move(client, fen)

    create_provider.assert_not_called()
    assert response.status_code == 200
    body = response.json()
    assert body["fen"] == fen
    assert body["move"] is None
    assert body["engine"] == "LLM"
    assert body["played_color"] == color
    assert body["metadata"]["error"] == {
        "code": "missing_api_key",
        "message": (
            "OpenAI is not configured. "
            "Add OPENAI_API_KEY to the environment."
        ),
        "retryable": False,
    }


def test_illegal_llm_move_is_returned_as_metadata_for_both_colors(
    client: TestClient,
    engine_position: tuple[str, str],
):
    color, fen = engine_position
    illegal_move = "e2e5" if color == "w" else "e7e4"
    provider = Mock()
    provider.choose_move.return_value = _provider_result(illegal_move)

    with patch.object(LLMEngine, "_create_provider", return_value=provider):
        response = _request_llm_move(client, fen)

    assert response.status_code == 200
    body = response.json()
    assert body["fen"] == fen
    assert body["move"] is None
    assert body["metadata"]["error"]["code"] == "illegal_move"


def test_llm_returns_domain_error_without_calling_provider_for_both_colors(
    client: TestClient,
    no_legal_moves_position: tuple[str, str],
):
    _, fen = no_legal_moves_position
    provider = Mock()

    with patch.object(LLMEngine, "_create_provider", return_value=provider):
        response = _request_llm_move(client, fen)

    assert response.status_code == 400
    assert response.json() == {"detail": "No legal moves"}
    provider.choose_move.assert_not_called()


@pytest.mark.parametrize(
    ("metadata", "field"),
    [
        ({"model": "test-model"}, "provider"),
        ({"provider": "openai"}, "model"),
        ({"provider": "unsupported", "model": "test-model"}, "provider"),
        (
            {
                "provider": "openai",
                "model": "test-model",
                "reasoningEffort": "extreme",
            },
            "reasoningEffort",
        ),
        (
            {
                "provider": "openai",
                "model": "test-model",
                "temperature": -0.1,
            },
            "temperature",
        ),
        (
            {
                "provider": "openai",
                "model": "test-model",
                "temperature": 2.1,
            },
            "temperature",
        ),
        (
            {
                "provider": "openai",
                "model": "test-model",
                "maxOutputTokens": 0,
            },
            "maxOutputTokens",
        ),
    ],
)
def test_llm_rejects_invalid_settings_for_both_colors(
    client: TestClient,
    engine_position: tuple[str, str],
    metadata: dict,
    field: str,
):
    _, fen = engine_position

    response = client.post(
        ENGINE_MOVE_URL,
        json={"fen": fen, "engine": "llm", "metadata": metadata},
    )

    assert response.status_code == 400
    assert response.json()["detail"].startswith(f"metadata.{field}:")


def test_llm_rejects_unknown_metadata_for_both_colors(
    client: TestClient,
    engine_position: tuple[str, str],
):
    _, fen = engine_position
    metadata = {**LLM_METADATA, "extra": True, "typo": 2}

    response = client.post(
        ENGINE_MOVE_URL,
        json={"fen": fen, "engine": "llm", "metadata": metadata},
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Unknown metadata field(s) for llm: extra, typo"
    }
