import time
from tokenize import generate_tokens

import pytest

from app.chess.board_mailbox import BoardMailbox as Board
from app.chess.move_mailbox import MoveMailBoxGenerator as MoveGenerator
from tests.chess.move_generator_cases import TEST_POSITIONS
from app.chess.static import *
from app.chess.utils import piece_flag_to_str, piece_str_to_flag, to_uci


# -----------------------------
# Functional correctness tests
# -----------------------------
def test_piece_flags():
    pieces = ["p", "P", "b", "B", "n", "N", "R", "r", "k", "K", "q", "Q"]
    for p in pieces:
        flag = piece_str_to_flag(p)
        p_n = piece_flag_to_str(flag)
        assert p_n == p


def test_black_pawn_moves():
    fen = "8/8/3pkp2/4P3/4Kp2/8/8/8 b - - 0 1"
    possible_moves = 8
    board = Board()
    board.from_fen(fen)

    generator = MoveGenerator(board)
    moves = generator.legal_moves()

    assert len(moves) == possible_moves


def test_black_pawn_moves_2():
    fen = "4k2r/8/8/8/8/8/8/4K3 b k - 0 1"
    possible_moves = 15
    board = Board()
    board.from_fen(fen)

    generator = MoveGenerator(board)
    moves = generator.legal_moves()

    assert len(moves) == possible_moves


def test_check_castling_in_check_kingside():
    fen = "2r1kr2/8/8/8/8/8/8/R3K2R w KQ - 0 1"
    possible_moves = 22
    board = Board()
    board.from_fen(fen)

    generator = MoveGenerator(board)
    moves = generator.legal_moves()
    for m in moves:
        print(to_uci(m))

    assert len(moves) == possible_moves


def test_check_castling_in_check_queenside():
    fen = "3rkr2/8/8/8/8/8/8/R3K2R w KQ - 0 1"
    possible_moves = 20
    board = Board()
    board.from_fen(fen)

    generator = MoveGenerator(board)
    moves = generator.legal_moves()

    assert len(moves) == possible_moves


def test_promotion_2():
    fen = "2n5/PPPk4/1n6/8/8/8/4Kppp/5N1N w - - 0 1"
    possible_moves = 24
    board = Board()
    board.from_fen(fen)

    generator = MoveGenerator(board)
    moves = generator.legal_moves()

    assert len(moves) == possible_moves


def test_in_check():
    fen = "8/1k6/P7/8/3r4/8/6Kp/8 b - - 0 1"
    possible_moves = 8
    board = Board()
    board.from_fen(fen)

    generator = MoveGenerator(board)
    moves = generator.legal_moves()

    assert len(moves) == possible_moves


from app.chess.utils import sq, rank_x, file_y


def tetst_pawn_block():
    fen = "r3k2r/8/8/8/8/8/8/2R1K2R w Kkq - 0 1"

    m = (sq(1, 3), sq(3, 3), 0)
    possible_moves = 3
    board = Board()
    board.from_fen(fen)

    generator = MoveGenerator(board)
    n_m = []
    m_m = generator.legal_moves()
    for m in generator.legal_moves():
        xy, nxy, flags = m
        print(f"{rank_x(xy)}, {file_y(xy)} - {rank_x(nxy)}, {file_y(nxy)}")
        generator.apply(m)
        n_m = generator.legal_moves()
        # print(f"possible moves: {len(n_m)}")
        fen = board.to_fen()
        for n in n_m:
            generator.apply(n)
            generator.undo(n)

        generator.undo(m)

    assert len(n_m) == possible_moves


def test_promotion():
    fen = "8/8/8/8/k7/8/K6p/8 b - - 0 1"
    possible_moves = 7
    board = Board()
    board.from_fen(fen)

    generator = MoveGenerator(board)
    moves = generator.legal_moves()

    assert len(moves) == possible_moves


def test_black_pawn_moves_3():
    fen = "4k3/4p3/4N3/8/8/8/8/7K b - - 0 1"
    possible_moves = 2
    board = Board()
    board.from_fen(fen)

    generator = MoveGenerator(board)
    moves = generator.legal_moves()
    for m in moves:
        print(to_uci(m))
    assert len(moves) == possible_moves


def test_cm_white():
    fen = "rnbqkbnr/ppppp2p/8/1B3ppQ/4P3/8/PPPP1PPP/RNB1K1NR b KQkq - 1 3"
    board = Board()
    board.from_fen(fen)

    generator = MoveGenerator(board)
    moves = generator.legal_moves()
    assert board.is_checkmate()
    assert board.is_checkmate()


def test_mg():
    fen = "rnbqkb1r/pppp1ppp/5n2/3Pp3/8/8/PPP1PPPP/RNBQKBNR w KQkq e6 0 3"
    board = Board()
    board.from_fen(fen)
    gen = MoveGenerator(board)
    moves = gen.legal_moves()
    for m in moves:
        gen.apply(m)
        gen.undo(m)
        print(to_uci(m))

    assert 30 == len(moves)


@pytest.mark.parametrize("name", TEST_POSITIONS.keys())
def test_legal_moves_basic(name):
    pos = TEST_POSITIONS[name]
    board = Board()
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
