import time
import pytest

from app.chess.board_array import BoardArray
from app.chess.move_array import MoveGenerator
from tests.chess.move_generator_cases import TEST_POSITIONS


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
    if name == "checkmate_white":
        a = 33
    if pos["is_checkmate"] is not None:
        assert board.is_checkmate(board.active_color) == pos["is_checkmate"], (
            f"{name}: expected checkmate = {pos["is_checkmate"]}"
        )
    if pos["is_stalemate"] is not None:
        assert board.is_stalemate(board.active_color) == pos["is_stalemate"], (
            f"{name}: expected stalemate = {pos["is_stalemate"]}"
        )
    if pos["is_threefold_rep"] is not None:
        assert board.is_threefold_repetition() == pos["is_threefold_rep"], (
            f"{name}: expected is_threefold_rep = {pos["is_threefold_rep"]}"
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
