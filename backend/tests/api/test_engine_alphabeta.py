from fastapi.testclient import TestClient

from app.chess.board_mailbox import BoardMailbox
from app.chess.move_mailbox import MoveMailBoxGenerator
from app.chess.utils import to_uci

ENGINE_MOVE_URL = "/api/v1/engine/move"


def _request_alphabeta_move(
    client: TestClient,
    fen: str,
    *,
    depth: int | None = 1,
    seed: int | None = 17,
):
    metadata = {}
    if depth is not None:
        metadata["depth"] = depth
    if seed is not None:
        metadata["seed"] = seed

    return client.post(
        ENGINE_MOVE_URL,
        json={"fen": fen, "engine": "alphabeta", "metadata": metadata},
    )


def test_alphabeta_move_response_contract_for_both_colors(
    client: TestClient,
    engine_position: tuple[str, str],
):
    color, fen = engine_position
    board = BoardMailbox()
    board.from_fen(fen)
    legal_moves = {to_uci(move) for move in MoveMailBoxGenerator(board).legal_moves()}

    response = _request_alphabeta_move(client, fen)

    assert response.status_code == 200
    body = response.json()
    assert body["move"] in legal_moves
    assert body["engine"] == "Alpha Beta Engine"
    assert body["played_color"] == color
    assert body["metadata"]["depth"] == 1
    assert body["metadata"]["seed"] == 17
    assert isinstance(body["metadata"]["evaluation"], int | float)
    for key in (
        "nodes",
        "cutoffs",
        "first_move_cutoffs",
        "tt_hits",
        "quiesce_calls",
    ):
        assert isinstance(body["metadata"][key], int)
        assert body["metadata"][key] >= 0
    assert set(body["metadata"]) == {
        "depth",
        "seed",
        "evaluation",
        "nodes",
        "cutoffs",
        "first_move_cutoffs",
        "tt_hits",
        "quiesce_calls",
    }
    assert body["status"] == "ok"

    MoveMailBoxGenerator(board).apply_uci(body["move"])
    assert body["fen"] == board.to_fen()
    assert body["fen"] != fen


def test_alphabeta_move_is_deterministic_for_both_colors(
    client: TestClient,
    engine_position: tuple[str, str],
):
    _, fen = engine_position

    first = _request_alphabeta_move(client, fen, seed=29)
    second = _request_alphabeta_move(client, fen, seed=29)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json() == second.json()


def test_alphabeta_move_uses_default_depth_for_both_colors(
    client: TestClient,
    engine_position: tuple[str, str],
):
    color, fen = engine_position

    response = _request_alphabeta_move(client, fen, depth=None, seed=None)

    assert response.status_code == 200
    body = response.json()
    assert body["played_color"] == color
    assert body["move"] is not None
    assert body["metadata"]["depth"] == 4
    assert body["metadata"]["seed"] is None
    assert set(body["metadata"]) == {
        "depth",
        "seed",
        "evaluation",
        "nodes",
        "cutoffs",
        "first_move_cutoffs",
        "tt_hits",
        "quiesce_calls",
    }


def test_alphabeta_move_returns_domain_error_when_no_move_exists_for_both_colors(
    client: TestClient,
    no_legal_moves_position: tuple[str, str],
):
    _, fen = no_legal_moves_position

    response = _request_alphabeta_move(client, fen)

    assert response.status_code == 400
    assert response.json() == {"detail": "No legal moves"}


def test_alphabeta_move_rejects_invalid_depth_for_both_colors(
    client: TestClient,
    engine_position: tuple[str, str],
):
    _, fen = engine_position

    for invalid_depth, expected_detail in (
        ("1", "metadata.depth must be an integer"),
        (True, "metadata.depth must be an integer"),
        (0, "metadata.depth must be greater than 0"),
        (-1, "metadata.depth must be greater than 0"),
    ):
        response = client.post(
            ENGINE_MOVE_URL,
            json={
                "fen": fen,
                "engine": "alphabeta",
                "metadata": {"depth": invalid_depth},
            },
        )

        assert response.status_code == 400
        assert response.json() == {"detail": expected_detail}


def test_alphabeta_move_rejects_invalid_seed_for_both_colors(
    client: TestClient,
    engine_position: tuple[str, str],
):
    _, fen = engine_position

    for invalid_seed in ("17", True):
        response = client.post(
            ENGINE_MOVE_URL,
            json={
                "fen": fen,
                "engine": "alphabeta",
                "metadata": {"depth": 1, "seed": invalid_seed},
            },
        )

        assert response.status_code == 400
        assert response.json() == {"detail": "metadata.seed must be an integer"}


def test_alphabeta_move_rejects_invalid_fen_for_both_colors(
    client: TestClient,
    engine_position: tuple[str, str],
):
    color, _ = engine_position
    invalid_fen = f"8/8/8/8/8/8/8/9 {color} - - 0 1"

    response = _request_alphabeta_move(client, invalid_fen)

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid board layout"}


def test_alphabeta_move_rejects_unknown_metadata_for_both_colors(
    client: TestClient,
    engine_position: tuple[str, str],
):
    _, fen = engine_position

    response = client.post(
        ENGINE_MOVE_URL,
        json={
            "fen": fen,
            "engine": "alphabeta",
            "metadata": {"depth": 1, "extra": True, "typo": 2},
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Unknown metadata field(s) for alphabeta: extra, typo"
    }
