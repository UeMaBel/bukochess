import pytest
from app.chess.utils import int_tuple_to_notation, notation_to_int_tuple


def test_int_tuple_to_notation():
    assert int_tuple_to_notation((0, 0)) == "a8"
    assert int_tuple_to_notation((4, 4)) == "e4"
    assert int_tuple_to_notation((7, 7)) == "h1"


def test_notation_to_int_tuple():
    assert notation_to_int_tuple("a8") == (0, 0)
    assert notation_to_int_tuple("e4") == (4, 4)
    assert notation_to_int_tuple("h1") == (7, 7)
