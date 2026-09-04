from app.chess.board_mailbox import BoardMailbox
from app.chess.engines.models import EngineResult
from app.chess.engines.random_engine import RandomEngine
from app.chess.move_mailbox import MoveMailBoxGenerator
from app.chess.utils import to_uci

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


def _board(fen: str = START_FEN) -> BoardMailbox:
    board = BoardMailbox()
    board.from_fen(fen)
    return board


def test_random_engine_returns_engine_result_with_metadata():
    board = _board()
    legal_moves = {to_uci(move) for move in MoveMailBoxGenerator(board).legal_moves()}

    result = RandomEngine(seed=7).choose_move(board)

    assert isinstance(result, EngineResult)
    assert result.move in legal_moves
    assert result.engine_name == "Random Engine"
    assert result.played_color == "w"
    assert result.metadata == {"seed": 7}


def test_random_engine_is_deterministic_with_seed():
    first = RandomEngine(seed=11).choose_move(_board())
    second = RandomEngine(seed=11).choose_move(_board())

    assert first.move == second.move


def test_random_engine_reports_black_as_played_color():
    board = _board(
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR b KQkq - 0 1"
    )

    result = RandomEngine(seed=1).choose_move(board)

    assert result.played_color == "b"


def test_random_engine_does_not_mutate_board():
    board = _board()
    fen_before = board.to_fen()
    hash_before = board.hash

    RandomEngine(seed=3).choose_move(board)

    assert board.to_fen() == fen_before
    assert board.hash == hash_before
    assert board.undo_stack == []


def test_random_engine_returns_none_without_legal_moves():
    board = _board("R6k/5Q2/7K/8/8/8/8/8 b - - 0 1")

    result = RandomEngine(seed=1).choose_move(board)

    assert result is None
