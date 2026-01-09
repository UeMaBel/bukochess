import pytest
from app.chess.board_mailbox import BoardMailbox as Board
from app.chess.move_flags import FLAG_PROMOTION, FLAG_PROMO_Q, FLAG_PROMO_N, FLAG_NONE
from app.chess.move_mailbox import MoveMailBoxGenerator as MoveGenerator
from app.chess.static import PAWN, WHITE, BLACK, QUEEN, KNIGHT, ROOK, BISHOP


def test_pawn_promotion_to_queen():
    # White pawn ready to promote
    board = Board()
    board.from_fen("8/P7/8/8/8/8/8/8 w - - 0 1")  # Pawn on a7
    gen = MoveGenerator(board)
    move = (6 * 8, 7 * 8, FLAG_PROMO_Q)
    gen.apply(move)

    assert board.board[7 * 8] == (WHITE | QUEEN)
    assert board.board[6 * 8] == 0
    assert board.active_color == BLACK

    # Undo
    gen.undo(move)
    assert board.board[6 * 8] == (WHITE | PAWN)
    assert board.board[7 * 8] == 0
    assert board.active_color == WHITE


def test_pawn_promotion_to_knight():
    board = Board()
    board.from_fen("8/P7/8/8/8/8/8/8 w - - 0 1")  # Pawn on h7
    gen = MoveGenerator(board)
    move = (6 * 8, 7 * 8, FLAG_PROMO_N)  # h7 -> h8=N
    gen.apply(move)

    assert board.board[7 * 8] == (WHITE | KNIGHT)
    gen.undo(move)
    assert board.board[7 * 8] == 0
    assert board.board[6 * 8] == (WHITE | PAWN)


def test_en_passant_creation():
    board = Board()
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    board.from_fen(fen)  # Black pawn on a2
    gen = MoveGenerator(board)
    move = (8, 24, FLAG_NONE)
    gen.apply(move)

    assert board.to_fen() == fen


def test_black_pawn_promotion():
    board = Board()
    board.from_fen("8/8/8/8/8/8/p7/8 b - - 0 1")  # Black pawn on a2
    gen = MoveGenerator(board)
    move = (8, 0, FLAG_PROMO_Q)
    gen.apply(move)
    assert board.board[0] == (BLACK | QUEEN)
    assert board.board[8] == 0

    gen.undo(move)
    assert board.board[8] == (BLACK | PAWN)
    assert board.board[0] == 0
