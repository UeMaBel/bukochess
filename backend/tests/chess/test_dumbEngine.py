from app.chess.board_mailbox import BoardMailbox
from app.chess.engines.dumb_engine import DumbEngine
from app.chess.engines.models import EngineResult
from app.chess.move_mailbox import MoveMailBoxGenerator
from app.chess.utils import to_uci

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


def _board(fen: str = START_FEN) -> BoardMailbox:
    board = BoardMailbox()
    board.from_fen(fen)
    return board


def test_dumb_engine_returns_engine_result_with_metadata():
    board = _board()
    legal_moves = {to_uci(move) for move in MoveMailBoxGenerator(board).legal_moves()}

    result = DumbEngine(depth=1, seed=7).choose_move(board)

    assert isinstance(result, EngineResult)
    assert result.move in legal_moves
    assert result.engine_name == "Dumb Engine"
    assert result.played_color == "w"
    assert result.metadata == {"seed": 7, "depth": 1}


def test_dumb_engine_is_deterministic_with_seed():
    first = DumbEngine(depth=1, seed=11).choose_move(_board())
    second = DumbEngine(depth=1, seed=11).choose_move(_board())

    assert first.move == second.move


def test_dumb_engine_chooses_obvious_capture_for_white():
    board = _board("7k/8/8/8/8/8/q7/R3K3 w - - 0 1")

    result = DumbEngine(depth=1, seed=1).choose_move(board)

    assert result.move == "a1a2"


def test_dumb_engine_does_not_mutate_board():
    board = _board()
    fen_before = board.to_fen()
    hash_before = board.hash

    DumbEngine(depth=2, seed=3).choose_move(board)

    assert board.to_fen() == fen_before
    assert board.hash == hash_before
    assert board.undo_stack == []


def test_dumb_engine_returns_none_without_legal_moves():
    board = _board("R6k/5Q2/7K/8/8/8/8/8 b - - 0 1")

    result = DumbEngine(depth=1, seed=1).choose_move(board)

    assert result is None
