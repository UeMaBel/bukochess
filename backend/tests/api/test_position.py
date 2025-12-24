import pytest
from fastapi.testclient import TestClient
from app.main import app  # Your FastAPI app

from tests.chess.fen_cases import VALID_FENS, INVALID_FENS

client = TestClient(app)

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


# ---------------------------
# /fen endpoint
# ---------------------------

@pytest.mark.parametrize("name,fen", VALID_FENS.items())
def test_fen_import_valid(name, fen):
    response = client.post("/api/v1/position/fen", json={"fen": fen})
    assert response.status_code == 200
    data = response.json()
    assert data["fen"] == fen
    assert len(data["board"]) == 8
    assert all(len(row) == 8 for row in data["board"])


@pytest.mark.parametrize("name,fen", INVALID_FENS.items())
def test_fen_import_invalid(name, fen):
    response = client.post("/api/v1/position/fen", json={"fen": fen})
    assert response.status_code == 400 or response.status_code == 422
    # Optional: check error message content
    data = response.json()
    assert "detail" in data


# ---------------------------
# /validate endpoint
# ---------------------------

@pytest.mark.parametrize("name,fen", VALID_FENS.items())
def test_validate_fen_valid(name, fen):
    response = client.post("/api/v1/position/validate", json={"fen": fen})
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["message"] is None


@pytest.mark.parametrize("name,fen", INVALID_FENS.items())
def test_validate_fen_invalid(name, fen):
    response = client.post("/api/v1/position/validate", json={"fen": fen})
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert data["message"] is not None


def test_legal_moves_from_e2():
    resp = client.post(
        "/api/v1/position/legal-moves",
        json={
            "fen": START_FEN,
            "square": "e2",
        },
    )

    assert resp.status_code == 200
    data = resp.json()

    assert "moves" in data
    assert "e2e4" in data["moves"]
    assert "e2e3" in data["moves"]
    assert len(data["moves"]) == 2


def test_legal_moves_start_position():
    resp = client.post("/api/v1/position/legal-moves", json={
        "fen": START_FEN,
        "square": ""
    })
    assert resp.status_code == 200
    data = resp.json()
    moves = data["moves"]
    assert len(moves) == 20


def test_legal_moves_invalid_fen():
    resp = client.post(
        "/api/v1/position/legal-moves",
        json={
            "fen": "invalid fen",
            "square": "e2",
        },
    )

    assert resp.status_code == 400
