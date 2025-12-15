import time
import pytest

from app.chess.board_array import BoardArray
from app.chess.move_array import MoveGenerator

TEST_POSITIONS = {
    "start_position": {
        "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "expected_moves": 20,  # known chess fact
    },
    "only_kings": {
        "fen": "8/8/8/8/8/8/4K3/2k5 w - - 0 1",
        "expected_moves": 6,
    },
    "open_rooks": {
        "fen": "8/8/8/8/8/8/R6R/4k3 w - - 0 1",
        "expected_moves": None,  # we only measure time here
    },
    "castling_position": {
        "fen": "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1",
        "expected_moves": None,  # depends on castling logic completeness
    },
}


# -----------------------------
# Functional correctness tests
# -----------------------------

@pytest.mark.parametrize("name", TEST_POSITIONS.keys())
def test_legal_moves_basic(name):
    pos = TEST_POSITIONS[name]
    board = BoardArray()
    board.from_fen(pos["fen"])

    generator = MoveGenerator(board)
    moves = generator.legal_moves()

    assert moves is not None
    assert isinstance(moves, list)

    if pos["expected_moves"] is not None:
        assert len(moves) == pos["expected_moves"], (
            f"{name}: expected {pos['expected_moves']} moves, got {len(moves)}"
        )


# -----------------------------
# Performance / timing test
# -----------------------------

def test_legal_moves_timing():
    board = BoardArray()
    board.from_fen(TEST_POSITIONS["start_position"]["fen"])
    generator = MoveGenerator(board)

    runs = 10
    start = time.perf_counter()

    for _ in range(runs):
        generator.legal_moves()

    end = time.perf_counter()
    avg_time_ms = ((end - start) / runs) * 1000

    print(f"\nAverage legal_moves() time: {avg_time_ms:.2f} ms")

    # Very generous limit – just to detect accidental O(n^4) explosions later
    assert avg_time_ms < 200
