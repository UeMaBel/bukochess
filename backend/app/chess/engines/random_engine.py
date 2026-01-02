import random
from app.chess.board_array import BoardArray
from app.chess.move_array_deprecated import MoveArray, MoveGenerator
from app.chess.engines.base import Engine


class RandomEngine(Engine):

    def __init__(self, seed: int | None = None):
        self._rng = random.Random(seed)

    def choose_move(self, board: BoardArray) -> MoveArray | None:
        generator = MoveGenerator(board)
        moves = generator.legal_moves()

        if not moves:
            return None

        return self._rng.choice(moves)
