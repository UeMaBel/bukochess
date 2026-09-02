from fastapi.testclient import TestClient


ENGINE_MOVE_URL = "/api/v1/engine/move"


def test_unknown_engine_is_rejected_for_both_colors(
    client: TestClient,
    engine_position: tuple[str, str],
):
    _, fen = engine_position

    response = client.post(
        ENGINE_MOVE_URL,
        json={"fen": fen, "engine": "does-not-exist", "metadata": {}},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Unknown engine: does-not-exist"}
