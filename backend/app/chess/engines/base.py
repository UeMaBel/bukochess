from abc import ABC, abstractmethod
from app.chess.board_array import BoardArray
from app.chess.move_array_deprecated import MoveArray


class Engine(ABC):
    @abstractmethod
    def choose_move(self, board: BoardArray) -> str | None:
        """
        Returns a move for the given board.
        Return None if no legal moves exist.
        """
        pass
