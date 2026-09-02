import pytest

from app.chess.board_mailbox import BoardMailbox


@pytest.mark.parametrize(
    ("fen", "expected"),
    [
        pytest.param(
            "8/8/8/8/8/8/8/4K2k w - - 0 1",
            True,
            id="king-versus-king",
        ),
        pytest.param(
            "8/8/8/8/8/8/8/2B1K2k w - - 0 1",
            True,
            id="bishop-versus-king",
        ),
        pytest.param(
            "8/8/8/8/8/8/8/2N1K2k w - - 0 1",
            True,
            id="knight-versus-king",
        ),
        pytest.param(
            "8/8/8/8/8/8/5b1B/4K2k w - - 0 1",
            True,
            id="same-color-bishops",
        ),
        pytest.param(
            "8/8/8/8/8/8/b6B/4K2k w - - 0 1",
            False,
            id="different-color-bishops-far-apart",
        ),
        pytest.param(
            "8/8/8/8/8/8/6bB/4K2k w - - 0 1",
            False,
            id="different-color-bishops-adjacent",
        ),
        pytest.param(
            "8/8/8/8/8/8/8/R3K2k w - - 0 1",
            False,
            id="rook-versus-king",
        ),
        pytest.param(
            "8/8/8/8/8/8/8/2BNK2k w - - 0 1",
            False,
            id="bishop-and-knight-versus-king",
        ),
    ],
)
def test_insufficient_material(fen: str, expected: bool):
    board = BoardMailbox()
    board.from_fen(fen)

    assert board.is_insufficient_material() is expected
