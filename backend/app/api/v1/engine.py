from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.chess.board_mailbox import BoardMailbox as Board
from app.chess.engines.alphabeta import AlphaBeta
from app.chess.engines.dumb_engine import DumbEngine
from app.chess.engines.random_engine import RandomEngine
from app.chess.move_mailbox import MoveMailBoxGenerator as MoveGenerator
from app.core.exceptions import BukochessException
from app.chess.engines.llm_engine import LLMEngine
from app.ai.settings import LLMSettings

router = APIRouter(tags=["engine"])


class EngineMoveRequest(BaseModel):
    fen: str
    engine: str = "random"
    metadata: dict[str, Any] = Field(default_factory=dict)


class EngineMoveResponse(BaseModel):
    fen: str
    move: str
    status: str
    engine: str
    played_color: str
    metadata: dict[str, Any] = Field(default_factory=dict)


def _optional_int(metadata: dict[str, Any], key: str) -> int | None:
    value = metadata.get(key)
    if value is None:
        return None

    # bool is a subclass of int in Python, but should not be accepted here.
    if isinstance(value, bool) or not isinstance(value, int):
        raise BukochessException(f"metadata.{key} must be an integer")

    return value


def _positive_int(
        metadata: dict[str, Any],
        key: str,
        *,
        default: int | None = None,
) -> int:
    value = _optional_int(metadata, key)

    if value is None:
        if default is None:
            raise BukochessException(f"metadata.{key} is required")
        value = default

    if value < 1:
        raise BukochessException(f"metadata.{key} must be greater than 0")

    return value


def _string(metadata: dict[str, Any], key: str, default: str | None = None) -> str:
    value = metadata.get(key)
    if value is None:
        value = default
    if value is None: value = ""
    return str(value)


def _float(metadata: dict[str, Any], key: str, default: float | None = None) -> float:
    value = metadata.get(key)
    if value is None:
        value = default

    if not isinstance(value, float):
        raise BukochessException(f"metadata.{key} must be an integer")

    return value


def _boolean(metadata: dict[str, Any], key: str, default: bool | None = None) -> bool:
    value = metadata.get(key)
    if value is None:
        value = default

    if not isinstance(value, bool):
        raise BukochessException(f"metadata.{key} must be an integer")

    return value


def _positive_float(metadata: dict[str, Any], key: str, default: float | None = None) -> float:
    value = _float(metadata, key)
    if value is None:
        value = default
    if value < 0:
        raise BukochessException(f"metadata.{key} must be greater than 0")
    return value


def _create_engine(req: EngineMoveRequest):
    """
    Create an engine from the stable request contract.

    `fen` and `engine` stay top-level. Everything engine-specific lives in
    `metadata`, so adding another engine does not require changing the API
    request model.
    """
    if req.engine == "random":
        seed = _optional_int(req.metadata, "seed")
        engine = RandomEngine(seed=seed)
        settings = {"seed": seed}

    elif req.engine == "dumb":
        depth = _positive_int(req.metadata, "depth")
        seed = _optional_int(req.metadata, "seed")
        engine = DumbEngine(depth=depth, seed=seed)
        settings = {
            "depth": depth,
            "seed": seed,
        }

    elif req.engine == "alphabeta":
        # AlphaBeta already has depth=4 as its own default, so the API can
        # expose the same default rather than making depth globally required.
        depth = _positive_int(req.metadata, "depth", default=4)
        seed = _optional_int(req.metadata, "seed")
        engine = AlphaBeta(depth=depth, seed=seed)
        settings = {
            "depth": depth,
            "seed": seed,
        }
    elif req.engine == "llm":
        llm_settings = LLMSettings.model_validate(req.metadata)
        engine = LLMEngine(llm_settings)

        settings = llm_settings.model_dump(
            by_alias=True,
        )

    else:
        raise BukochessException(f"Unknown engine: {req.engine}")

    # Do not echo null settings unless they were explicitly supplied.
    settings = {
        key: value
        for key, value in settings.items()
        if value is not None or key in req.metadata
    }

    return engine, settings


def _response_metadata(
        engine_id: str,
        engine,
        settings: dict[str, Any],
) -> dict[str, Any]:
    """
    Echo the resolved engine settings and append only metadata that is useful
    for that engine.

    Later an LLM engine can add e.g. provider/model to the settings and
    latency/tokens/confidence/explanation to the result without changing the
    response model.
    """
    metadata: dict[str, Any] = {
        **settings,
        "name": engine.engine_name,
    }

    if engine_id == "dumb":
        metadata.update(
            evaluation=engine.evaluation,
            depth=engine.depth,
        )

    elif engine_id == "alphabeta":
        metadata.update(
            evaluation=engine.evaluation,
            depth=engine.depth,
            nodes=engine.nodes,
            cutoffs=engine.cutoffs,
            tt_hits=engine.tt_hits,
            quiesce_calls=engine.quiesce_calls,
        )
    elif engine_id == "llm":
        print("hallo welt2")

    return metadata


@router.post("/move", response_model=EngineMoveResponse)
def engine_move(req: EngineMoveRequest):
    board = Board()

    try:
        board.from_fen(req.fen)
    except ValueError as exc:
        raise BukochessException(str(exc)) from exc

    engine, settings = _create_engine(req)

    move = engine.choose_move(board)
    if move is None:
        raise BukochessException("No legal moves")

    generator = MoveGenerator(board)
    generator.apply_uci(move)

    return EngineMoveResponse(
        fen=board.to_fen(),
        move=move,
        status=board.get_game_state(),
        engine=req.engine,
        played_color=engine.played_color,
        metadata=_response_metadata(req.engine, engine, settings),
    )
