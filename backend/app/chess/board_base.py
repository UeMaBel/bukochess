from abc import ABC, abstractmethod

class BoardBase(ABC):
    """
    Abstract base class for all chess board representations.
    """

    @abstractmethod
    def from_fen(self, fen: str):
        """Load a board from a FEN string"""
        pass

    @abstractmethod
    def to_fen(self) -> str:
        """Convert internal board to FEN string"""
        pass

    @abstractmethod
    def generate_moves(self) -> list[str]:
        """Return pseudo-legal moves for current position"""
        pass

    @abstractmethod
    def make_move(self, move: str):
        """Apply a move to the board"""
        pass

    @abstractmethod
    def is_in_check(self, color: str) -> bool:
        """Return True if color is in check"""
        pass
