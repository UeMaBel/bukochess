from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.chess.board_mailbox import BoardMailbox as Board
from app.chess.move_mailbox import MoveMailBoxGenerator as MoveGenerator
from app.chess.static import WHITE
from app.chess.utils import from_uci_move, to_uci
from app.core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["game"])


class MoveRequest(BaseModel):
    fen: str
    move: str  # "e2e4"


class MoveResponse(BaseModel):
    fen: str
    status: str
    legal_moves: list[str]


class MoveResponseFast(BaseModel):
    fen: str
    played_color: str
    engine: str
    move: str


def _parse_board(fen: str) -> Board:
    board = Board()
    try:
        board.from_fen(fen)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return board


@router.post("/fast-move", response_model=MoveResponseFast)
def make_fast_move(req: MoveRequest):
    board = _parse_board(req.fen)
    try:
        move = from_uci_move(req.move)
    except ValueError:
        raise HTTPException(status_code=400, detail="invalid move format")

    generator = MoveGenerator(board)

    generator.apply_uci(req.move)

    return {
        "fen": board.to_fen(),
        "played_color": "b" if board.active_color == WHITE else "w",
        "engine": "Human",
        "move": req.move,
    }


@router.post("/move", response_model=MoveResponse)
def make_move(req: MoveRequest):
    board = _parse_board(req.fen)
    try:
        move = from_uci_move(req.move)
    except ValueError:
        raise HTTPException(status_code=400, detail="invalid move format")

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
    board = _parse_board(req.fen)

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
