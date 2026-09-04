from app.chess.board_mailbox import BoardMailbox
from app.chess.move_mailbox import MoveMailBoxGenerator
from app.chess.utils import sq


def test_threefold_repetition_knight_shuffle():
    board = BoardMailbox()
    board.from_fen("4k1n1/8/8/8/8/8/8/4K1N1 w - - 0 1")
    gen = MoveMailBoxGenerator(board)

    moves = [
        (sq(0, 6), sq(2, 5), 0),  # Ng1-f3
        (sq(7, 6), sq(5, 5), 0),  # Ng8-f6
        (sq(2, 5), sq(0, 6), 0),  # Nf3-g1
        (sq(5, 5), sq(7, 6), 0),  # Nf6-g8
    ]

    # Repeat sequence twice (initial position counts as first)
    for _ in range(2):
        for move in moves:
            gen.apply(move)

    assert board.is_threefold_repetition() is True


def test_twofold_repetition_is_not_draw():
    board = BoardMailbox()
    board.from_fen("4k1n1/8/8/8/8/8/8/4K1N1 w - - 0 1")
    gen = MoveMailBoxGenerator(board)

    moves = [
        (sq(0, 6), sq(2, 5), 0),
        (sq(7, 6), sq(5, 5), 0),
        (sq(2, 5), sq(0, 6), 0),
        (sq(5, 5), sq(7, 6), 0),
    ]

    for move in moves:
        gen.apply(move)

    assert board.is_threefold_repetition() is False


def test_repetition_castling_rights_matter():
    board = BoardMailbox()
    board.from_fen("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
    gen = MoveMailBoxGenerator(board)

    # Ra1-b1
    move1 = (sq(0, 0), sq(0, 1), 0)
    # Rb1-a1
    move2 = (sq(0, 1), sq(0, 0), 0)

    gen.apply(move1)
    gen.apply(move2)

    # Castling rights changed → no repetition
    assert board.is_threefold_repetition() is False


def test_repetition_en_passant_matters():
    board = BoardMailbox()
    board.from_fen("8/8/8/3pP3/8/8/8/8 w - d6 0 1")
    gen = MoveMailBoxGenerator(board)

    # e5-e6
    move = (sq(4, 4), sq(5, 4), 0)

    gen.apply(move)
    gen.undo(move)

    # En passant square changed/reset → no repetition
    assert board.is_threefold_repetition() is False
