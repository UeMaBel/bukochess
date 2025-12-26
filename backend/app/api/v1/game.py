from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.logger import get_logger
from app.core.exceptions import BukochessException
from app.chess.board_array import BoardArray
from app.chess.move_array import MoveArray, MoveGenerator
from app.chess.engines.random_engine import RandomEngine

logger = get_logger(__name__)
router = APIRouter(tags=["game"])


class MoveRequest(BaseModel):
    fen: str
    move: str  # "e2e4"


class MoveResponse(BaseModel):
    fen: str
    status: str
    legal_moves: int


@router.post("/move", response_model=MoveResponse)
def make_move(req: MoveRequest):
    board = BoardArray()
    ok, msg = board.from_fen(req.fen)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)

    try:
        move = MoveArray.from_uci(req.move)
    except ValueError:
        raise HTTPException(status_code=400, detail="invalid move format")

    generator = MoveGenerator(board)
    legal_moves = generator.legal_moves()

    move_found = False
    for m in legal_moves:
        if str(m) == req.move:
            move_found = True
            break
    if not move_found:
        raise HTTPException(status_code=400, detail="illegal move")

    undo = move.apply(board)

    status = board.get_game_state()

    return {
        "fen": board.to_fen(),
        "status": status,
        "legal_moves": len(MoveGenerator(board).legal_moves()),
    }


class GameStatusRequest(BaseModel):
    fen: str


class GameStatusResponse(BaseModel):
    fen: str
    active_color: str
    in_check: bool
    status: str


@router.post("/status", response_model=GameStatusResponse)
def game_status(req: GameStatusRequest):
    board = BoardArray()
    try:
        board.from_fen(req.fen)
    except ValueError as e:
        raise BukochessException(str(e))

    active = board.active_color

    in_check = board.is_king_in_check(active)

    status = board.get_game_state()

    return GameStatusResponse(
        fen=req.fen,
        active_color=active,
        in_check=in_check,
        status=status
    )
