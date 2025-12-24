from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


def test_engine_random_move():
    res = client.post("/api/v1/engine/move", json={
        "fen": START_FEN,
        "engine": "random",
        "seed": 1
    })
    assert res.status_code == 200
    assert "move" in res.json()
    assert "fen" in res.json()
