from abc import ABC, abstractmethod

from app.chess.board_mailbox import BoardMailbox
from app.chess.engines.models import EngineResult


class Engine(ABC):
    def __init__(self):
        self.evaluation: float = 0
        self.nps: int = -99
        self.pv: list[str] = []
        self.depth = 0
        self.nodes = 0
        self.engine_name: str = ""
        self.played_color: str = ""

    @abstractmethod
    def choose_move(self, board: BoardMailbox) -> EngineResult | None:
        """
        Returns a move for the given board.
        Return None if no legal moves exist.
        """
        pass
