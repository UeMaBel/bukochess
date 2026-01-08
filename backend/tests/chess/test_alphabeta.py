import pytest
from app.chess.move_mailbox import MoveMailBoxGenerator as MoveGenerator, BoardMailbox as Board
from app.chess.engines.alphabeta import AlphaBeta
from app.chess.utils import to_uci


def create_test(fen: str, deepness: int | None = None):
    board = Board()
    board.from_fen(fen)
    gen = MoveGenerator(board)
    return AlphaBeta(deepness), gen


def test_mate_in_one():
    fen = "rnbqkb1r/ppppp2p/8/5p2/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1"
    best_move = "d1h5"
    eng, gen = create_test(fen, 2)
    m = eng.choose_move(gen.board)
    assert m == best_move


def test_check_logis():
    fen = "r1bq2r1/b4pk1/p1pp1p2/1p2pP2/1P2P1PB/3P4/1PPQ2P1/R3K2R w - - 0 1"
    best_move = "d2h6"
    black_move = "g7h6"
    second_move = "h4f6"
    eng, gen = create_test(fen, 2)
    gen.apply_uci(best_move)
    gen.apply_uci(black_move)
    gen.apply_uci(second_move)
    moves = gen.legal_moves()

    assert len(moves) == 0


def test_mate_in_two():
    fen = "r1bq2r1/b4pk1/p1pp1p2/1p2pP2/1P2P1PB/3P4/1PPQ2P1/R3K2R w - - 0 1"
    best_move = "d2h6"
    eng, gen = create_test(fen, 2)
    m = eng.choose_move(gen.board)
    assert m == best_move


def test_mate_in_three():
    fen = "2r3k1/p4p2/3Rp2p/1p2P1pK/8/1P4P1/P3Q2P/1q6 b - - 0 1"
    best_move = "b1g6"
    eng, gen = create_test(fen, 2)
    m = eng.choose_move(gen.board)
    assert m == best_move
