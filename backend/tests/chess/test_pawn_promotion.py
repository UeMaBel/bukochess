import pytest
from app.chess.board_array import BoardArray
from app.chess.move_flags import FLAG_PROMOTION, FLAG_PROMO_Q, FLAG_PROMO_N
from app.chess.move_tuple import MoveTupleGenerator


def test_pawn_promotion_to_queen():
    # White pawn ready to promote
    board = BoardArray()
    board.from_fen("8/P7/8/8/8/8/8/8 w - - 0 1")  # Pawn on a7
    gen = MoveTupleGenerator(board)
    move = (8, 0, FLAG_PROMO_Q)
    gen.apply(move)

    assert board.board[0][0] == "Q"  # pawn promoted to queen
    assert board.board[1][0] == ""
    assert board.active_color == "b"

    # Undo
    gen.undo(move)
    assert board.board[1][0] == "P"
    assert board.board[0][0] == ""
    assert board.active_color == "w"


def test_pawn_promotion_to_knight():
    board = BoardArray()
    board.from_fen("8/P7/8/8/8/8/8/8 w - - 0 1")  # Pawn on h7
    gen = MoveTupleGenerator(board)
    move = (8, 0, FLAG_PROMO_N)  # h7 -> h8=N
    gen.apply(move)

    assert board.board[0][0] == "N"
    gen.undo(move)
    assert board.board[1][0] == "P"


def test_pawn_default_promotion():
    board = BoardArray()
    board.from_fen("8/P7/8/8/8/8/8/8 w - - 0 1")
    gen = MoveTupleGenerator(board)
    move = (8, 0, FLAG_PROMO_Q)
    gen.apply(move)

    assert board.board[0][0] == "Q"  # default queen
    gen.undo(move)
    assert board.board[1][0] == "P"


def test_black_pawn_promotion():
    board = BoardArray()
    board.from_fen("8/8/8/8/8/8/p7/8 b - - 0 1")  # Black pawn on a2
    gen = MoveTupleGenerator(board)
    move = (48, 56, FLAG_PROMO_Q)
    gen.apply(move)
    assert board.board[7][0] == "q"
    assert board.board[6][0] == ""

    gen.undo(move)
    assert board.board[6][0] == "p"
    assert board.board[7][0] == ""
