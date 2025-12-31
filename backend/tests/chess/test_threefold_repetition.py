from app.chess.board_array import BoardArray
from app.chess.move_array import MoveArray
from app.chess.perft import perft


def test_threefold_repetition_knight_shuffle():
    board = BoardArray()
    board.from_fen("4k1n1/8/8/8/8/8/8/4K1N1 w - - 0 1")

    moves = [
        MoveArray((7, 6), (5, 5)),  # Ng1-f3
        MoveArray((0, 6), (2, 5)),  # Ng8-f6
        MoveArray((5, 5), (7, 6)),  # Nf3-g1
        MoveArray((2, 5), (0, 6)),  # Nf6-g8
    ]

    # Repeat sequence twice (initial position counts as first)
    for _ in range(2):
        for move in moves:
            move.apply(board)

    assert board.is_threefold_repetition() is True


def test_twofold_repetition_is_not_draw():
    board = BoardArray()
    board.from_fen("4k1n1/8/8/8/8/8/8/4K1N1 w - - 0 1")

    moves = [
        MoveArray((7, 6), (5, 5)),
        MoveArray((0, 6), (2, 5)),
        MoveArray((5, 5), (7, 6)),
        MoveArray((2, 5), (0, 6)),
    ]

    for move in moves:
        move.apply(board)

    assert board.is_threefold_repetition() is False


def test_repetition_castling_rights_matter():
    board = BoardArray()
    board.from_fen("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")

    move1 = MoveArray((7, 0), (7, 1))  # Ra1-b1
    move2 = MoveArray((7, 1), (7, 0))  # Rb1-a1

    move1.apply(board)
    move2.apply(board)

    # Castling rights changed → no repetition
    assert board.is_threefold_repetition() is False


def test_repetition_en_passant_matters():
    board = BoardArray()
    board.from_fen("8/8/8/3pP3/8/8/8/8 w - d6 0 1")

    move = MoveArray((3, 4), (4, 4))  # e5-e6
    undo = move.apply(board)
    move.undo(board, undo)

    # En passant square changed/reset → no repetition
    assert board.is_threefold_repetition() is False


def test_repetition_undo_restorekjs_counts():
    board = BoardArray()
    board.from_fen(" 8/8/k7/p7/P7/K7/8/8 b - - 0 1")

    erg = perft(board, 2)
    assert erg == 9


def test_repetition_undo_restores_counts():
    board = BoardArray()
    board.from_fen("4k3/8/8/8/8/8/8/4K3 w - - 0 1")

    initial_key = board.create_repetition_key()
    initial_count = board.position_counts[initial_key]

    move = MoveArray((7, 4), (6, 4))  # Ke1-e2
    undo = move.apply(board)
    move.undo(board, undo)

    assert board.position_counts[initial_key] == initial_count
