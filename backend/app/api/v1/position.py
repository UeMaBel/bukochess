from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.core.exceptions import BukochessException
from app.core.logger import get_logger
from app.chess.board_array import BoardArray
from app.chess.utils import rank_x, file_y, to_uci

logger = get_logger(__name__)
router = APIRouter(tags=["position"])


# ------------------------------
# Request / Response Schemas
# ------------------------------

class FENRequest(BaseModel):
    fen: str


class BoardResponse(BaseModel):
    board: list[list[str]]
    fen: str


class ValidationResponse(BaseModel):
    fen: str
    valid: bool
    message: str | None = None


# ------------------------------
# Routes
# ------------------------------

@router.post("/fen", response_model=BoardResponse)
def import_fen(req: FENRequest):
    fen = req.fen.strip()
    logger.info(f"Importing FEN: {fen}")

    board_obj = BoardArray()
    try:
        board_obj.from_fen(fen)
    except Exception as e:
        raise BukochessException(str(e))

    return BoardResponse(board=board_obj.board, fen=fen)


@router.post("/validate", response_model=ValidationResponse)
def validate_fen_endpoint(req: FENRequest):
    fen = req.fen.strip()
    logger.info(f"Validating FEN: {fen}")

    try:
        valid, message = BoardArray.validate_fen(fen)
    except Exception as e:
        raise BukochessException(str(e))

    return ValidationResponse(fen=fen, valid=valid, message=message)


from typing import List
from app.chess.move_tuple import MoveTupleGenerator
from app.chess.utils import notation_to_int_tuple


class LegalMovesRequest(BaseModel):
    fen: str
    square: str  # e.g. "e2"


class LegalMovesResponse(BaseModel):
    moves: List[str]


@router.post("/legal-moves")
def legal_moves(req: LegalMovesRequest):
    board = BoardArray()
    try:
        board.from_fen(req.fen)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    generator = MoveTupleGenerator(board)
    moves = generator.legal_moves()
    final_moves = []
    if req.square != "":
        from_tuple = notation_to_int_tuple(req.square)

        for m in moves:
            xy, nxy, flags = m
            if rank_x(xy) == from_tuple[0] and file_y(xy) == from_tuple[1]:
                final_moves.append(m)
    else:
        final_moves = moves
    m_str = []
    for m in final_moves:
        m_str.append(to_uci(m))
    return {
        "moves": m_str,
    }
