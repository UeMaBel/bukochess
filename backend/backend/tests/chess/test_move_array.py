import pytest
from app.chess.board_mailbox import BoardMailbox as Board


@pytest.fixture
def start_board():
    board = Board()
    board.from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    return board


@pytest.fixture
def empty_castling_board():
    board = Board()
    board.from_fen("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
    return board
