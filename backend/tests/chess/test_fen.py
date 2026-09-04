import pytest

from app.chess.board_mailbox import BoardMailbox
from tests.chess.fen_cases import (
    ADVANCED_INVALID_FENS,
    ADVANCED_VALID_FENS,
    INVALID_FENS,
    VALID_FENS,
)


@pytest.mark.parametrize("name,fen", VALID_FENS.items())
def test_validate_fen_valid(name, fen):
    valid, msg = BoardMailbox.validate_fen(fen)
    assert valid is True, f"{name} should be valid"
    assert msg is None


@pytest.mark.parametrize("name,fen", INVALID_FENS.items())
def test_validate_fen_invalid(name, fen):
    valid, msg = BoardMailbox.validate_fen(fen)
    assert valid is False, f"{name} should be invalid"
    assert msg is not None


@pytest.mark.parametrize("name,fen", ADVANCED_VALID_FENS.items())
def test_validate_fen_advanced_valid(name, fen):
    valid, msg = BoardMailbox.validate_fen(fen)
    assert valid is True, f"{name} should be valid"
    assert msg is None


@pytest.mark.parametrize("name,fen", ADVANCED_INVALID_FENS.items())
def test_validate_fen_advanced_invalid(name, fen):
    valid, msg = BoardMailbox.validate_fen(fen)
    assert valid is False, f"{name} should be invalid"
    assert msg is not None


@pytest.mark.parametrize("name,fen", VALID_FENS.items())
def test_fen_round_trip(name, fen):
    board = BoardMailbox()
    board.from_fen(fen)
    out_fen = board.to_fen()

    valid, msg = BoardMailbox.validate_fen(out_fen)
    assert valid is True, f"Round-trip failed for {name}: {msg}"
