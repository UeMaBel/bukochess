from abc import ABC, abstractmethod
import re

BOARD_RE = re.compile(r'^([PNBRQKpnbrqk1-8]{1,8}/){7}[PNBRQKpnbrqk1-8]{1,8}$')
ACTIVE_RE = re.compile(r'^[wb]$')
CASTLING_RE = re.compile(r'^(-|[KQkq]{1,4})$')
ENPASSANT_RE = re.compile(r'^(-|[a-h][36])$')
HALFMOVE_RE = re.compile(r'^\d+$')
FULLMOVE_RE = re.compile(r'^[1-9]\d*$')
PAWN_RE = re.compile(r"[pP]")


class BoardBase(ABC):
    """
    Abstract base class for all chess board representations.
    """

    @staticmethod
    def validate_fen(fen: str) -> tuple[bool, str | None]:
        parts = fen.strip().split(" ")

        if len(parts) != 6:
            return False, f"FEN must contain exactly 6 fields, not {len(parts)}"

        board, active, castling, ep, halfmove, fullmove = parts

        if not BOARD_RE.match(board):
            return False, "Invalid board layout"

        board_rows = board.split("/")
        if PAWN_RE.match(board_rows[0]) or PAWN_RE.match(board_rows[7]):
            return False, "Invalid Pawn: Pawn on first or last row"
        for row in board_rows:
            count = 0
            for c in row:
                if c.isdigit():
                    count += int(c)
                else:
                    count += 1
            if count != 8:
                return False, "Invalid board sum"

        if not ACTIVE_RE.match(active):
            return False, "Active color must be 'w' or 'b'"

        if not CASTLING_RE.match(castling):
            return False, "Invalid castling rights"

        if not ENPASSANT_RE.match(ep):
            return False, "Invalid en passant square"

        if not HALFMOVE_RE.match(halfmove):
            return False, "Halfmove clock must be a non-negative integer"

        if not FULLMOVE_RE.match(fullmove):
            return False, "Fullmove number must be a positive integer"

        return True, None

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
