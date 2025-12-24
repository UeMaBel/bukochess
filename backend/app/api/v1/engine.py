from fastapi import APIRouter
from pydantic import BaseModel
from app.chess.board_array import BoardArray
from app.chess.engines.random_engine import RandomEngine
from app.core.exceptions import BukochessException

router = APIRouter(tags=["engine"])


class EngineMoveRequest(BaseModel):
    fen: str
    engine: str = "random"
    seed: int | None = None


class EngineMoveResponse(BaseModel):
    fen: str
    move: str


@router.post("/move", response_model=EngineMoveResponse)
def engine_move(req: EngineMoveRequest):
    board = BoardArray()
    try:
        board.from_fen(req.fen)
    except ValueError as e:
        raise BukochessException(str(e))

    if req.engine == "random":
        engine = RandomEngine(seed=req.seed)
    else:
        raise BukochessException("Unknown engine")

    move = engine.choose_move(board)
    if move is None:
        raise BukochessException("No legal moves")

    undo = move.apply(board)

    return EngineMoveResponse(
        fen=board.to_fen(),
        move=str(move),
    )
