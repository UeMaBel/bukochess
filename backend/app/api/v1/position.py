from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.exceptions import BukochessException
from app.core.logger import get_logger
from app.chess.board_array import BoardArray

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
