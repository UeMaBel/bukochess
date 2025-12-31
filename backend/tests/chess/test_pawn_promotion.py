import pytest
from app.chess.board_array import BoardArray
from app.chess.move_array import MoveArray


def test_pawn_promotion_to_queen():
    # White pawn ready to promote
    board = BoardArray()
    board.from_fen("8/P7/8/8/8/8/8/8 w - - 0 1")  # Pawn on a7

    move = MoveArray(from_square=(1, 0), to_square=(0, 0), promotion="q")  # a7 -> a8=Q
    undo = move.apply(board)

    assert board.board[0][0] == "Q"  # pawn promoted to queen
    assert board.board[1][0] == ""
    assert board.active_color == "b"

    # Undo
    move.undo(board, undo)
    assert board.board[1][0] == "P"
    assert board.board[0][0] == ""
    assert board.active_color == "w"


def test_pawn_promotion_to_knight():
    board = BoardArray()
    board.from_fen("7P/8/8/8/8/8/8/8 w - - 0 1")  # Pawn on h7

    move = MoveArray(from_square=(0, 7), to_square=(0, 7), promotion="n")  # h7 -> h8=N
    undo = move.apply(board)

    assert board.board[0][7] == "N"
    move.undo(board, undo)
    assert board.board[0][7] == "P"


def test_pawn_default_promotion():
    board = BoardArray()
    board.from_fen("8/P7/8/8/8/8/8/8 w - - 0 1")

    move = MoveArray(from_square=(1, 0), to_square=(0, 0), promotion="q")
    undo = move.apply(board)

    assert board.board[0][0] == "Q"  # default queen
    move.undo(board, undo)
    assert board.board[1][0] == "P"


def test_black_pawn_promotion():
    board = BoardArray()
    board.from_fen("8/8/8/8/8/8/p7/8 b - - 0 1")  # Black pawn on a2

    move = MoveArray(from_square=(6, 0), to_square=(7, 0), promotion="q")  # a2 -> a1=Q
    undo = move.apply(board)

    assert board.board[7][0] == "q"
    assert board.board[6][0] == ""

    move.undo(board, undo)
    assert board.board[6][0] == "p"
    assert board.board[7][0] == ""
