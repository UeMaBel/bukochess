from fastapi import APIRouter
from pydantic import BaseModel
from app.chess.board_mailbox import BoardMailbox as Board
from app.chess.engines.random_engine import RandomEngine
from app.chess.engines.dumb_engine import DumbEngine
from app.chess.engines.alphabeta import AlphaBeta
from app.chess.move_mailbox import MoveMailBoxGenerator as MoveGenerator
from app.core.exceptions import BukochessException

router = APIRouter(tags=["engine"])


class EngineMoveRequest(BaseModel):
    fen: str
    engine: str = "random"
    seed: int | None = None


class EngineMoveResponse(BaseModel):
    fen: str
    move: str
    status: str


@router.post("/move", response_model=EngineMoveResponse)
def engine_move(req: EngineMoveRequest):
    board = Board()
    try:
        board.from_fen(req.fen)
    except ValueError as e:
        raise BukochessException(str(e))
    if req.engine == "random":
        engine = RandomEngine(seed=req.seed)
    elif req.engine == "dumb":
        engine = DumbEngine(seed=req.seed)
    elif req.engine == "alphabeta":
        engine = AlphaBeta(seed=req.seed)
    else:
        raise BukochessException("Unknown engine")

    generator = MoveGenerator(board)
    move = engine.choose_move(board)
    if move is None:
        raise BukochessException("No legal moves")

    generator.apply_uci(move)
    status = board.get_game_state()

    return EngineMoveResponse(
        fen=board.to_fen(),
        move=str(move),
        status=status,
    )
