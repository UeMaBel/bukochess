import pytest
from app.chess.board_mailbox import BoardMailbox as Board
from app.chess.move_flags import FLAG_NONE, FLAG_CAPTURE, FLAG_EN_PASSANT
from app.chess.move_mailbox import MoveMailBoxGenerator as MoveGenerator
from app.chess.static import PAWN, WHITE, BLACK
from app.chess.utils import sq, square_to_notation


def test_apply_undo_normal_move():
    # Standard starting position
    board = Board()
    board.from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    gen = MoveGenerator(board)
    move = (sq(1, 4), sq(3, 4), FLAG_NONE)  # e2 -> e4
    gen.apply(move)

    # Assertions
    assert board.board[3 * 8 + 4] == (WHITE | PAWN)
    assert board.board[1 * 8 + 4] == 0
    assert board.active_color == BLACK

    # Undo
    gen.undo(move)
    assert board.board[1 * 8 + 4] == (WHITE | PAWN)
    assert board.board[3 * 8 + 4] == 0
    assert board.active_color == WHITE


def test_apply_undo_capture():
    board = Board()
    board.from_fen("8/8/8/3p4/4P3/8/8/8 w - - 0 1")
    gen = MoveGenerator(board)

    # e4 captures d5
    move = (3 * 8 + 4, 4 * 8 + 3, FLAG_CAPTURE)
    gen.apply(move)

    # After apply
    assert board.board[4 * 8 + 3] == (WHITE | PAWN)
    assert board.board[3 * 8 + 4] == 0
    assert board.active_color == BLACK

    # Undo
    gen.undo(move)
    assert board.board[3 * 8 + 4] == (WHITE | PAWN)
    assert board.board[4 * 8 + 3] == (BLACK | PAWN)
    assert board.active_color == WHITE


def test_apply_undo_nested():
    # Use FEN to set up en passant scenario
    start_fen = "r1bqkbnr/pppp1ppp/2n5/3Pp3/8/8/PPP1PPPP/RNBQKBNR w KQkq e6 0 3"
    board = Board()
    board.from_fen(start_fen)  # White to move
    gen = MoveGenerator(board)
    start_hash = board.hash
    moves = gen.legal_moves()

    for m in moves:
        gen.apply(m)
        for n in gen.legal_moves():
            gen.apply(n)
            gen.undo(n)
        gen.undo(m)

    end_fen = board.to_fen()
    end_hash = board.hash
    assert start_fen == end_fen
    assert start_hash == end_hash


def test_apply_undo_en_passant():
    # Use FEN to set up en passant scenario
    board = Board()
    board.from_fen("r1bqkbnr/pppp1ppp/2n5/3Pp3/8/8/PPP1PPPP/RNBQKBNR w KQkq e6 0 3")  # White to move
    gen = MoveGenerator(board)
    # White pawn moves d5->d6 (already en passant target set to e6 in FEN, meaning en passant has to go away)
    move1 = (sq(4, 3), sq(5, 3), FLAG_NONE)
    gen.apply(move1)
    assert 1 > board.en_passant
    # assert board.en_passant is None or board.en_passant == "-"  # updated internally
    gen.undo(move1)
    assert "e6" == square_to_notation(board.en_passant)
