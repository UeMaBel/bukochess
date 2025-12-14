import pytest
from app.chess.board_array import BoardArray
from tests.chess.fen_cases import VALID_FENS, INVALID_FENS


@pytest.mark.parametrize("name,fen", VALID_FENS.items())
def test_validate_fen_valid(name, fen):
    valid, msg = BoardArray.validate_fen(fen)
    assert valid is True, f"{name} should be valid"
    assert msg is None


@pytest.mark.parametrize("name,fen", INVALID_FENS.items())
def test_validate_fen_invalid(name, fen):
    valid, msg = BoardArray.validate_fen(fen)
    assert valid is False, f"{name} should be invalid"
    assert msg is not None


@pytest.mark.parametrize("name,fen", VALID_FENS.items())
def test_fen_round_trip(name, fen):
    board = BoardArray()
    board.from_fen(fen)
    out_fen = board.to_fen()

    print(f"original: {fen} - out: {out_fen}")

    valid, msg = BoardArray.validate_fen(out_fen)
    assert valid is True, f"Round-trip failed for {name}: {msg}"
