import pytest
from app.chess.board_array import BoardArray
from app.chess.move_flags import FLAG_NONE, FLAG_CAPTURE, FLAG_EN_PASSANT
from app.chess.move_tuple import MoveTupleGenerator
from app.chess.utils import sq


def test_apply_undo_normal_move():
    # Standard starting position
    board = BoardArray()
    board.from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    gen = MoveTupleGenerator(board)
    move = (sq(6, 4), sq(4, 4), FLAG_NONE)  # e2 -> e4
    gen.apply(move)

    # Assertions
    assert board.board[4][4] == "P"
    assert board.board[6][4] == ""
    assert board.active_color == "b"

    # Undo
    gen.undo(move)
    assert board.board[6][4] == "P"
    assert board.board[4][4] == ""
    assert board.active_color == "w"


def test_apply_undo_capture():
    # Use FEN to set up white pawn on e4, black pawn on d5
    board = BoardArray()
    board.from_fen("8/8/8/3p4/4P3/8/8/8 w - - 0 1")
    gen = MoveTupleGenerator(board)
    move = (36, 27, FLAG_CAPTURE)  # e4 captures d5
    gen.apply(move)

    assert board.board[3][3] == "P"
    assert board.board[4][4] == ""
    assert board.active_color == "b"

    # Undo
    gen.undo(move)
    assert board.board[4][4] == "P"
    assert board.board[3][3] == "p"
    assert board.active_color == "w"


def test_apply_undo_nested():
    # Use FEN to set up en passant scenario
    start_fen = "r1bqkbnr/pppp1ppp/2n5/3Pp3/8/8/PPP1PPPP/RNBQKBNR w KQkq e6 0 3"
    board = BoardArray()
    board.from_fen(start_fen)  # White to move
    gen = MoveTupleGenerator(board)
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
    print(end_fen)
    assert start_fen == end_fen
    assert start_hash == end_hash


def test_apply_undo_en_passant():
    # Use FEN to set up en passant scenario
    board = BoardArray()
    board.from_fen("r1bqkbnr/pppp1ppp/2n5/3Pp3/8/8/PPP1PPPP/RNBQKBNR w KQkq e6 0 3")  # White to move
    gen = MoveTupleGenerator(board)
    # White pawn moves d5->d6 (already en passant target set to e6 in FEN, meaning en passant has to go away)
    move1 = (sq(3, 3), sq(2, 3), FLAG_NONE)
    gen.apply(move1)
    assert board.en_passant is None or board.en_passant == "-"  # updated internally
    gen.undo(move1)
    assert board.en_passant == "e6"
