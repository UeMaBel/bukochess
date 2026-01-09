from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.logger import get_logger
from app.core.exceptions import BukochessException
from app.chess.board_mailbox import BoardMailbox as Board
from app.chess.move_mailbox import MoveMailBoxGenerator as MoveGenerator
from app.chess.utils import from_uci_move, to_uci
from app.chess.engines.random_engine import RandomEngine
from app.chess.static import WHITE

logger = get_logger(__name__)
router = APIRouter(tags=["game"])


class MoveRequest(BaseModel):
    fen: str
    move: str  # "e2e4"


class MoveResponse(BaseModel):
    fen: str
    status: str
    legal_moves: list[str]


@router.post("/move", response_model=MoveResponse)
def make_move(req: MoveRequest):
    board = Board()
    ok, msg = board.from_fen(req.fen)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    try:
        move = from_uci_move(req.move)
    except ValueError:
        raise HTTPException(status_code=400, detail="invalid move format")

    print(req.move)
    print(to_uci(move))

    generator = MoveGenerator(board)
    legal_moves = generator.legal_moves()

    move_found = False
    for m in legal_moves:
        if to_uci(m) == req.move:
            move_found = True
            move = m
            break
    if not move_found:
        raise HTTPException(status_code=400, detail="illegal move")

    generator.apply_uci(req.move)

    status = board.get_game_state()
    legal_moves = MoveGenerator(board).legal_moves()
    legal_moves_str = []
    for m in legal_moves:
        legal_moves_str.append(to_uci(m))
    print(board.to_fen())

    return {
        "fen": board.to_fen(),
        "status": status,
        "legal_moves": legal_moves_str
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
    board = Board()
    try:
        board.from_fen(req.fen)
    except ValueError as e:
        raise BukochessException(str(e))

    active = board.active_color

    in_check = board.is_king_in_check

    status = board.get_game_state()
    active_color = "w" if active == WHITE else "b"

    return GameStatusResponse(
        fen=req.fen,
        active_color=active_color,
        in_check=in_check,
        status=status
    )
