from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


def test_make_legal_move():
    resp = client.post(
        "/api/v1/game/move",
        json={
            "fen": START_FEN,
            "move": "e2e4",
        },
    )

    assert resp.status_code == 200
    data = resp.json()

    assert "fen" in data
    assert data["status"] in ("ok", "check")
    assert data["legal_moves"] > 0


def test_status_ongoing():
    res = client.post("/api/v1/game/status", json={
        "fen": START_FEN
    })
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_status_stalemate():
    res = client.post("/api/v1/game/status", json={
        "fen": "7k/5Q2/7K/8/8/8/8/8 b - - 0 1"
    })
    assert res.json()["status"] == "stalemate"


def test_status_checkmate():
    res = client.post("/api/v1/game/status", json={
        "fen": "R6k/5Q2/7K/8/8/8/8/8 b - - 0 1"
    })
    assert res.json()["status"] == "checkmate"


def test_illegal_move():
    resp = client.post(
        "/api/v1/game/move",
        json={
            "fen": START_FEN,
            "move": "e2e5",
        },
    )

    assert resp.status_code == 400


def test_invalid_move_format():
    resp = client.post(
        "/api/v1/game/move",
        json={
            "fen": START_FEN,
            "move": "e9e4",
        },
    )

    assert resp.status_code == 400
