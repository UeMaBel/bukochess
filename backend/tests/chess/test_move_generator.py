import time
import pytest

from app.chess.board_array import BoardArray
from app.chess.move_array import MoveGenerator
from tests.chess.move_generator_cases import TEST_POSITIONS


# -----------------------------
# Functional correctness tests
# -----------------------------

def test_black_pawn_moves():
    fen = "8/8/3pkp2/4P3/4Kp2/8/8/8 b - - 0 1"
    possible_moves = 8
    board = BoardArray()
    board.from_fen(fen)

    generator = MoveGenerator(board)
    moves = generator.legal_moves()

    assert len(moves) == possible_moves


def test_black_pawn_moves_2():
    fen = "k7/8/8/4p3/3P4/8/8/K7 b - - 0 1"
    possible_moves = 5
    board = BoardArray()
    board.from_fen(fen)

    generator = MoveGenerator(board)
    moves = generator.legal_moves()

    assert len(moves) == possible_moves


def test_check_castling_in_check_kingside():
    fen = "2r1kr2/8/8/8/8/8/8/R3K2R w KQ - 0 1"
    possible_moves = 22
    board = BoardArray()
    board.from_fen(fen)

    generator = MoveGenerator(board)
    moves = generator.legal_moves()

    assert len(moves) == possible_moves


def test_check_castling_in_check_queenside():
    fen = "3rkr2/8/8/8/8/8/8/R3K2R w KQ - 0 1"
    possible_moves = 20
    board = BoardArray()
    board.from_fen(fen)

    generator = MoveGenerator(board)
    moves = generator.legal_moves()

    assert len(moves) == possible_moves


def test_promotion_2():
    fen = "2n5/PPPk4/1n6/8/8/8/4Kppp/5N1N w - - 0 1"
    possible_moves = 24
    board = BoardArray()
    board.from_fen(fen)

    generator = MoveGenerator(board)
    moves = generator.legal_moves()

    assert len(moves) == possible_moves


def test_in_check():
    fen = "8/1k6/P7/8/3r4/8/6Kp/8 b - - 0 1"
    possible_moves = 8
    board = BoardArray()
    board.from_fen(fen)

    generator = MoveGenerator(board)
    moves = generator.legal_moves()

    assert len(moves) == possible_moves


def test_promotion():
    fen = "8/8/8/8/k7/8/K6p/8 b - - 0 1"
    possible_moves = 7
    board = BoardArray()
    board.from_fen(fen)

    generator = MoveGenerator(board)
    moves = generator.legal_moves()

    assert len(moves) == possible_moves


def test_black_pawn_moves_3():
    fen = "4k3/4p3/4N3/8/8/8/8/7K b - - 0 1"
    possible_moves = 2
    board = BoardArray()
    board.from_fen(fen)

    generator = MoveGenerator(board)
    moves = generator.legal_moves()

    assert len(moves) == possible_moves


def test_cm_white():
    fen = "rnbqkbnr/ppppp2p/8/1B3ppQ/4P3/8/PPPP1PPP/RNB1K1NR b KQkq - 1 3"
    board = BoardArray()
    board.from_fen(fen)

    generator = MoveGenerator(board)
    moves = generator.legal_moves()
    assert board.is_checkmate()
    assert board.is_checkmate()


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
    if pos["is_checkmate"] is not None:
        assert board.is_checkmate() == pos["is_checkmate"], (
            f"{name}: expected checkmate = {pos["is_checkmate"]}"
        )
    if pos["is_stalemate"] is not None:
        assert board.is_stalemate() == pos["is_stalemate"], (
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
