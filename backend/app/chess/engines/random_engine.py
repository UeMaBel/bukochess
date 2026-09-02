import random
from app.chess.board_mailbox import BoardMailbox as Board
from app.chess.move_mailbox import MoveMailBoxGenerator as Generator
from app.chess.engines.base import Engine
from app.chess.utils import to_uci
from app.chess.static import WHITE, BLACK
from app.chess.engines.models import EngineResult


class RandomEngine(Engine):

    def __init__(self, seed: int | None = None):
        super().__init__()
        self.engine_name = "Random Engine"
        self.seed = seed
        self._rng = random.Random(seed)

    def choose_move(self, board: Board) -> EngineResult:
        generator = Generator(board)
        moves = generator.legal_moves()

        if not moves:
            return None
        self.played_color = "w" if board.active_color == WHITE else "b"
        return EngineResult(
            engine_name=self.engine_name,
            move=to_uci(self._rng.choice(moves)),
            played_color=self.played_color,
            metadata={"seed": self.seed}
        )
