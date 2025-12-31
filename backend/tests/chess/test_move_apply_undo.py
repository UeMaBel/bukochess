import pytest
from app.chess.board_array import BoardArray
from app.chess.move_array import MoveArray, MoveGenerator


def test_apply_undo_normal_move():
    # Standard starting position
    board = BoardArray()
    board.from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

    move = MoveArray(from_square=(6, 4), to_square=(4, 4))  # e2 -> e4
    undo = move.apply(board)

    # Assertions
    assert board.board[4][4] == "P"
    assert board.board[6][4] == ""
    assert board.active_color == "b"

    # Undo
    move.undo(board, undo)
    assert board.board[6][4] == "P"
    assert board.board[4][4] == ""
    assert board.active_color == "w"


def test_apply_undo_capture():
    # Use FEN to set up white pawn on e4, black pawn on d5
    board = BoardArray()
    board.from_fen("8/8/8/3p4/4P3/8/8/8 w - - 0 1")

    move = MoveArray(from_square=(4, 4), to_square=(3, 3))  # e4 captures d5
    undo = move.apply(board)

    assert board.board[3][3] == "P"
    assert board.board[4][4] == ""
    assert board.active_color == "b"

    # Undo
    move.undo(board, undo)
    assert board.board[4][4] == "P"
    assert board.board[3][3] == "p"
    assert board.active_color == "w"


def test_casling():
    fen = "r3k1r1/8/8/8/8/8/8/R3K2R b KQq - 0 1"
    possible_moves = 25
    board = BoardArray()
    board.from_fen(fen)

    move1 = MoveArray(from_square=(0, 0), to_square=(0, 1))
    undo1 = move1.apply(board)
    move1.undo(board, undo1)
    move1.apply(board)

    generator = MoveGenerator(board)
    moves = generator.legal_moves()

    for m in moves:
        print(str(m))

    assert len(moves) == possible_moves


def test_apply_undo_nested():
    # Use FEN to set up en passant scenario
    start_fen = "r1bqkbnr/pppp1ppp/2n5/3Pp3/8/8/PPP1PPPP/RNBQKBNR w KQkq e6 0 3"
    board = BoardArray()
    board.from_fen(start_fen)  # White to move

    start_hash = board.hash
    generator = MoveGenerator(board)
    moves = generator.legal_moves()

    for m in moves:
        undo = m.apply(board)
        new_generator = MoveGenerator(board)
        for n in new_generator.legal_moves():
            undo_n = n.apply(board)
            n.undo(board, undo_n)
        m.undo(board, undo)

    end_fen = board.to_fen()
    end_hash = board.hash
    print(end_fen)
    assert start_fen == end_fen
    assert start_hash == end_hash


def test_apply_undo_en_passant():
    # Use FEN to set up en passant scenario
    board = BoardArray()
    board.from_fen("r1bqkbnr/pppp1ppp/2n5/3Pp3/8/8/PPP1PPPP/RNBQKBNR w KQkq e6 0 3")  # White to move

    # White pawn moves d5->d6 (already en passant target set to e6 in FEN, meaning en passant has to go away)
    move1 = MoveArray(from_square=(3, 3), to_square=(2, 3))
    undo1 = move1.apply(board)  # undo, meaning en passant has to be back
    assert board.en_passant is None or board.en_passant == "-"  # updated internally
    move1.undo(board, undo1)
    assert board.en_passant == "e6"
