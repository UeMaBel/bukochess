import pytest
from app.chess.board_array import BoardArray


def test_k_vs_k():
    board = BoardArray()
    board.from_fen("8/8/8/8/8/8/8/4K2k w - - 0 1")
    assert board.is_insufficient_material()


def test_k_vs_k():
    board = BoardArray()
    board.from_fen("8/8/8/8/8/8/8/4K2k w - - 0 1")
    assert board.is_insufficient_material()


def test_k_vs_k():
    board = BoardArray()
    board.from_fen("8/8/8/8/8/8/8/4K2k w - - 0 1")
    assert board.is_insufficient_material()


def test_same_color_bishops():
    board = BoardArray()
    board.from_fen("8/8/8/8/8/8/6bB/4K2k w - - 0 1")
    assert board.is_insufficient_material()


def test_different_color_bishops():
    board = BoardArray()
    board.from_fen("8/8/8/8/8/8/b6B/4K2k w - - 0 1")
    assert not board.is_insufficient_material()


def test_different_color_bishops():
    board = BoardArray()
    board.from_fen("8/8/8/8/8/8/6bB/4K2k w - - 0 1")
    assert not board.is_insufficient_material()


def test_same_color_bishops():
    board = BoardArray()
    board.from_fen("8/8/8/8/8/8/5b1B/4K2k w - - 0 1")
    assert board.is_insufficient_material()
