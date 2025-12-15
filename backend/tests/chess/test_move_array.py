import pytest
from app.chess.board_array import BoardArray
from app.chess.move_array import MoveArray
from app.chess.move_array import is_pseudo_legal


@pytest.fixture
def start_board():
    board = BoardArray()
    board.from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    return board


def test_pawn_moves(start_board):
    # White pawn e2 -> e4 (double step)
    move = MoveArray((6, 4), (4, 4))  # row 6 = rank 2, column 4 = e
    valid, msg = is_pseudo_legal(start_board, move)
    assert valid, f"Expected e2-e4 to be legal, got: {msg}"

    # White pawn e2 -> e3 (single step)
    move = MoveArray((6, 4), (5, 4))
    valid, msg = is_pseudo_legal(start_board, move)
    assert valid, f"Expected e2-e3 to be legal, got: {msg}"

    # Illegal backward move
    move = MoveArray((6, 4), (7, 4))
    valid, msg = is_pseudo_legal(start_board, move)
    assert not valid


def test_knight_moves(start_board):
    # White knight g1 -> f3
    move = MoveArray((7, 6), (5, 5))
    valid, msg = is_pseudo_legal(start_board, move)
    assert valid, f"Expected g1-f3 to be legal, got: {msg}"

    # Illegal move
    move = MoveArray((7, 6), (5, 6))
    valid, msg = is_pseudo_legal(start_board, move)
    assert not valid


def test_rook_moves_blocked(start_board):
    # Rook a1 -> a3 blocked by pawn
    move = MoveArray((7, 0), (5, 0))
    valid, msg = is_pseudo_legal(start_board, move)
    assert not valid

    # Clear path (simulate pawn removed)
    start_board.board[6][0] = ""
    move = MoveArray((7, 0), (5, 0))
    valid, msg = is_pseudo_legal(start_board, move)
    assert valid


def test_bishop_moves(start_board):
    # Bishop f1 -> c4 blocked initially
    move = MoveArray((7, 5), (4, 2))
    valid, msg = is_pseudo_legal(start_board, move)
    assert not valid

    # Clear path
    start_board.board[6][4] = ""
    move = MoveArray((7, 5), (4, 2))
    valid, msg = is_pseudo_legal(start_board, move)
    assert valid


def test_queen_moves(start_board):
    # Queen d1 -> h5 blocked by own pieces
    move = MoveArray((7, 3), (3, 7))
    valid, msg = is_pseudo_legal(start_board, move)
    assert not valid

    # Clear path
    start_board.board[6][4] = ""
    start_board.board[5][5] = ""
    start_board.board[4][6] = ""
    move = MoveArray((7, 3), (3, 7))
    valid, msg = is_pseudo_legal(start_board, move)
    assert valid


def test_king_moves(start_board):
    # King e1 -> e2 blocked
    move = MoveArray((7, 4), (6, 4))
    valid, msg = is_pseudo_legal(start_board, move)
    assert not valid

    # Clear path
    start_board.board[6][4] = ""
    move = MoveArray((7, 4), (6, 4))
    valid, msg = is_pseudo_legal(start_board, move)

    assert valid


@pytest.fixture
def empty_castling_board():
    board = BoardArray()
    board.from_fen("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
    return board


def test_white_kingside_castling_pseudo_legal(empty_castling_board):
    # King e1 -> g1
    move = MoveArray((7, 4), (7, 6))
    valid, msg = is_pseudo_legal(empty_castling_board, move)
    assert valid, msg


def test_white_queenside_castling_pseudo_legal(empty_castling_board):
    # King e1 -> c1
    move = MoveArray((7, 4), (7, 2))
    valid, msg = is_pseudo_legal(empty_castling_board, move)
    assert valid, msg


def test_black_kingside_castling_pseudo_legal():
    board = BoardArray()
    board.from_fen("r3k2r/8/8/8/8/8/8/R3K2R b KQkq - 0 1")

    # King e8 -> g8
    move = MoveArray((0, 4), (0, 6))
    valid, msg = is_pseudo_legal(board, move)
    assert valid, msg


def test_black_queenside_castling_pseudo_legal():
    board = BoardArray()
    board.from_fen("r3k2r/8/8/8/8/8/8/R3K2R b KQkq - 0 1")

    # King e8 -> c8
    move = MoveArray((0, 4), (0, 2))
    valid, msg = is_pseudo_legal(board, move)
    assert valid, msg
