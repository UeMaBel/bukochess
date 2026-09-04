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
    assert len(data["legal_moves"]) > 0


def test_make_castle_move():
    resp = client.post(
        "/api/v1/game/move",
        json={
            "fen": "4k3/3r4/8/8/8/8/8/4K2R w K - 0 1",
            "move": "e1g1",
        },
    )

    assert resp.status_code == 200
    data = resp.json()

    assert data["fen"] == "4k3/3r4/8/8/8/8/8/5RK1 b - - 1 1"
    assert data["status"] in ("ok", "check")
    assert len(data["legal_moves"]) == 16


def test_status_ongoing():
    res = client.post("/api/v1/game/status", json={"fen": START_FEN})
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_status_stalemate():
    res = client.post(
        "/api/v1/game/status", json={"fen": "7k/5Q2/7K/8/8/8/8/8 b - - 0 1"}
    )
    assert res.json()["status"] == "stalemate"


def test_status_checkmate():
    res = client.post(
        "/api/v1/game/status", json={"fen": "R6k/5Q2/7K/8/8/8/8/8 b - - 0 1"}
    )
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


def test_fast_move_response_contract_for_both_colors(
    client: TestClient,
    engine_position: tuple[str, str],
):
    color, fen = engine_position
    move = "e2e4" if color == "w" else "e7e5"

    response = client.post(
        "/api/v1/game/fast-move",
        json={"fen": fen, "move": move},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["move"] == move
    assert body["played_color"] == color
    assert body["engine"] == "Human"
    assert body["fen"] != fen


def test_fast_move_rejects_invalid_format_for_both_colors(
    client: TestClient,
    engine_position: tuple[str, str],
):
    _, fen = engine_position

    response = client.post(
        "/api/v1/game/fast-move",
        json={"fen": fen, "move": "e9e4"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "invalid move format"}


def test_game_endpoints_reject_invalid_fen_for_both_colors(
    client: TestClient,
    engine_position: tuple[str, str],
):
    color, _ = engine_position
    invalid_fen = f"8/8/8/8/8/8/8/9 {color} - - 0 1"

    for endpoint, payload in (
        ("/api/v1/game/fast-move", {"fen": invalid_fen, "move": "e2e4"}),
        ("/api/v1/game/move", {"fen": invalid_fen, "move": "e2e4"}),
        ("/api/v1/game/status", {"fen": invalid_fen}),
    ):
        response = client.post(endpoint, json=payload)

        assert response.status_code == 400
        assert response.json() == {"detail": "Invalid board layout"}
