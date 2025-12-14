import pytest
from fastapi.testclient import TestClient
from app.main import app  # Your FastAPI app

from tests.chess.fen_cases import VALID_FENS, INVALID_FENS

client = TestClient(app)


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
