from typing import Optional, List, Tuple

from pydantic.v1.mypy import from_orm_callback

from app.chess.board_array import BoardArray


class MoveArray:
    """
    Represents a single chess move on a BoardArray.
    """

    def __init__(self, from_square: Tuple[int, int], to_square: Tuple[int, int], promotion: Optional[str] = None):
        """
        :param from_square: tuple (row, col) of starting square, 0-indexed
        :param to_square: tuple (row, col) of target square, 0-indexed
        :param promotion: optional promotion piece ('q', 'r', 'b', 'n')
        """
        self.from_square = from_square
        self.to_square = to_square
        self.promotion = promotion

        # Optional metadata
        self.captured_piece: Optional[str] = None
        self.castling: Optional[str] = None
        self.en_passant: bool = False

    def is_legal(self, board: BoardArray) -> Tuple[bool, Optional[str]]:
        """
        Validate if the move is legal on the given board.
        Returns (True, None) if legal, (False, reason) if not.
        """
        # TODO: implement piece movement rules, check legality
        return True, None

    def apply(self, board: BoardArray):
        """
        Apply the move to the board (updates BoardArray in-place).
        """
        # TODO: update board array, active color, castling rights, en passant, halfmove/fullmove counters
        pass


class MoveGenerator:
    """
    Generates all legal moves for a given BoardArray.
    """

    def __init__(self, board: BoardArray):
        self.board = board

    def legal_moves(self) -> List[MoveArray]:
        """
        Return a list of all legal moves for the current active color.
        """
        moves: List[MoveArray] = []

        # TODO: generate pseudo-legal moves first (piece movement rules)
        # TODO: filter out moves that leave own king in check

        return moves


def is_pseudo_legal(board: BoardArray, move: MoveArray) -> tuple[bool, str | None]:
    """
    Checks if a move is pseudo-legal
    """
    active_color = board.active_color
    # get pieces
    from_square_piece = board.board[move.from_square[0]][move.from_square[1]]
    from_x = move.from_square[0]
    from_y = move.from_square[1]
    to_square_piece = board.board[move.to_square[0]][move.to_square[1]]
    to_x = move.to_square[0]
    to_y = move.to_square[1]
    abs_x = abs(from_x - to_x)
    abs_y = abs(from_y - to_y)
    d_x = to_x - from_x
    d_y = to_y - from_y
    piece = from_square_piece.lower()
    direction = 1 if from_square_piece.isupper() else -1

    if from_x > 7 or from_y > 7 or to_x > 7 or to_y > 7 or from_x < 0 or from_y < 0 or to_y < 0 or to_x < 0:
        return False, "end of board"
    if from_square_piece == "":
        return False, "no piece selected"
    if active_color == "b" and from_square_piece.isupper():
        return False, "blacks turn"
    if active_color == "w" and not from_square_piece.isupper():
        return False, "whites turn"
    if to_square_piece != "":
        if to_square_piece.isupper() == from_square_piece.isupper():
            return False, "cant capture same color"
    # piece logics
    if piece == "k":  # KING
        # TODO: castling logic
        if abs_x > 1 or abs_y > 1:
            return False, "wrong king movement"

    elif piece == "q":  # QUEEN
        # TODO: sliding movement along ranks, files, diagonals
        pass

    elif piece == "r":  # ROOK
        # TODO: sliding movement
        pass

    elif piece == "b":  # BISHOP
        # TODO: sliding movement
        pass

    elif piece == "n":  # KNIGHT
        if (abs_x, abs_y) not in [(1, 2), (2, 1)]:
            return False, "illegal knight move"

    if from_square_piece.lower() == "p":  # PAWN
        if to_square_piece != "":  # capture
            if abs_x != 0 and abs_y == direction:
                return True, None
            else:
                return False, "illegal pawn capture"
        else:  # move forward
            if d_x == 0 and d_y == direction:
                return True, None
            start_row = 6 if from_square_piece.isupper() else 1
            if from_x == start_row and d_x == 0 and d_y == 2 * direction:
                return True, None
            return False, "illegal pawn move"

    return True, None
