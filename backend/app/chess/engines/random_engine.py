import random
from app.chess.board_mailbox import BoardMailbox as Board
from app.chess.move_mailbox import MoveMailBoxGenerator as Generator
from app.chess.engines.base import Engine
from app.chess.utils import to_uci


class RandomEngine(Engine):

    def __init__(self, seed: int | None = None):
        self._rng = random.Random(seed)

    def choose_move(self, board: Board) -> str:
        generator = Generator(board)
        moves = generator.legal_moves()

        if not moves:
            return None

        return to_uci(self._rng.choice(moves))
