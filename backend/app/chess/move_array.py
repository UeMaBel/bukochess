from typing import Optional, List, Tuple

from app.chess.board_array import BoardArray
from app.core.utils import measure_time


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

    @measure_time
    def legal_moves(self) -> List[MoveArray]:
        """
        Return a list of all legal moves for the current active color.
        """
        moves: List[MoveArray] = []
        active_color = self.board.active_color
        for from_x in range(0, 8):
            for from_y in range(0, 8):
                square = self.board.board[from_x][from_y]
                if square == "":
                    continue
                if active_color == "w" and square.islower():
                    continue
                if active_color == "b" and square.isupper():
                    continue
                for to_x in range(0, 8):
                    for to_y in range(0, 8):
                        move = MoveArray(from_square=(from_x, from_y), to_square=(to_x, to_y))
                        valid, _ = is_pseudo_legal(self.board, move)
                        if valid:
                            moves.append(move)

        # TODO: filter out moves that leave own king in check

        print(len(moves))

        return moves


class MoveInformation():
    def __init__(self, board: BoardArray, move: MoveArray):
        self.board = board
        self.move = move

        self.active_color = board.active_color
        self.from_square_piece = board.board[move.from_square[0]][move.from_square[1]]
        self.to_square_piece = board.board[move.to_square[0]][move.to_square[1]]
        self.piece = self.from_square_piece.lower()

        self.from_x = move.from_square[0]
        self.from_y = move.from_square[1]
        self.to_x = move.to_square[0]
        self.to_y = move.to_square[1]

        self.abs_dx = abs(self.from_x - self.to_x)
        self.abs_dy = abs(self.from_y - self.to_y)
        self.d_x = self.to_x - self.from_x
        self.d_y = self.to_y - self.from_y


def is_pseudo_legal(board: BoardArray, move: MoveArray) -> tuple[bool, str | None]:
    """
    Checks if a move is pseudo-legal
    """
    mi = MoveInformation(board, move)

    if mi.from_x > 7 or mi.from_y > 7 or mi.to_x > 7 or mi.to_y > 7 or mi.from_x < 0 or mi.from_y < 0 or mi.to_y < 0 or mi.to_x < 0:
        return False, "end of board"
    if mi.abs_dx == 0 and mi.abs_dy == 0:
        return False, "piece didnt move"
    if mi.from_square_piece == "":
        return False, "no piece selected"
    if mi.active_color == "b" and mi.from_square_piece.isupper():
        return False, "blacks turn"
    if mi.active_color == "w" and not mi.from_square_piece.isupper():
        return False, "whites turn"
    if mi.to_square_piece != "":
        if mi.to_square_piece.isupper() == mi.from_square_piece.isupper():
            return False, "cant capture same color"

    # piece logics
    if mi.piece == "k":  # KING
        return pseudo_king(mi)

    elif mi.piece == "q":  # QUEEN
        return pseudo_queen(mi)

    elif mi.piece == "r":  # ROOK
        return pseudo_rook(mi)

    elif mi.piece == "b":  # BISHOP
        return pseudo_bishop(mi)

    elif mi.piece == "n":  # KNIGHT
        return pseudo_knight(mi)

    if mi.piece == "p":  # PAWN
        return pseudo_pawn(mi)

    return True, None


def pseudo_king(mi: MoveInformation):
    # check if opponent king is next to to_field
    x_to_check = []
    y_to_check = []
    if mi.to_x != 0:
        x_to_check.append(mi.to_x - 1)
    if mi.to_x != 7:
        x_to_check.append(mi.to_x + 1)
    if mi.to_y != 0:
        y_to_check.append(mi.to_y - 1)
    if mi.to_y != 7:
        y_to_check.append(mi.to_y + 1)
    x_to_check.append(mi.to_x)
    y_to_check.append(mi.to_y)
    for x in x_to_check:
        for y in y_to_check:
            if x == mi.from_x and y == mi.from_y:
                continue
            if x == mi.to_x and y == mi.to_y:
                continue
            if mi.board.board[x][y].lower() == "k":
                return False, "king to close to enemy king"

    # castle logic
    if mi.abs_dx == 0 and mi.abs_dy == 2:
        is_white = mi.from_square_piece.isupper()
        rights = mi.board.castling_rights

        # kingside castle
        if mi.d_y > 0:
            if (is_white and "K" not in rights) or (not is_white and "k" not in rights):
                return False, "no castling rights"

            rook_y = 7
            path = [(mi.from_x, 5), (mi.from_x, 6)]

        # queenside castle
        else:
            if (is_white and "Q" not in rights) or (not is_white and "q" not in rights):
                return False, "no castling rights"

            rook_y = 0
            path = [(mi.from_x, 3), (mi.from_x, 2), (mi.from_x, 1)]

        rook_char = "R" if is_white else "r"
        if mi.board.board[mi.from_x][rook_y] != rook_char:
            return False, "rook missing for castling"

        for x, y in path:
            if mi.board.board[x][y] != "":
                return False, "piece in the way for castling"

        return True, None

    # normal king move
    if max(mi.abs_dx, mi.abs_dy) == 1:
        return True, None

    return False, "illegal king movement"


def pseudo_queen(mi: MoveInformation):
    # first check if diagonal or rank/file movement:
    if mi.abs_dx == mi.abs_dy:  # diagonal movement
        step_x = 1 if mi.d_x > 0 else -1
        step_y = 1 if mi.d_y > 0 else -1
        x, y = mi.from_x + step_x, mi.from_y + step_y
        while x != mi.to_x and y != mi.to_y:
            if mi.board.board[x][y] != "":
                return False, "piece in the way"
            x += step_x
            y += step_y
        return True, None
    if (mi.abs_dx == 0 and mi.abs_dy > 0) or (mi.abs_dx > 0 and mi.abs_dy == 0):  # rook movement
        if mi.abs_dx == 0:
            step = 1 if mi.d_y > 0 else -1
            for y in range(mi.from_y + step, mi.to_y, step):
                if mi.board.board[mi.from_x][y] != "":
                    return False, "piece in the way"
        elif mi.abs_dy == 0:
            step = 1 if mi.d_x > 0 else -1
            for x in range(mi.from_x + step, mi.to_x, step):
                if mi.board.board[x][mi.from_y] != "":
                    return False, "piece in the way"
        return True, None
    else:
        return False, "queen can only move ranks, files or diagonally"


def pseudo_rook(mi: MoveInformation):
    if mi.abs_dx > 0 and mi.abs_dy > 0:
        return False, "rook can only move ranks, or files"
    if mi.abs_dx == 0:
        step = 1 if mi.d_y > 0 else -1
        for y in range(mi.from_y + step, mi.to_y, step):
            if mi.board.board[mi.from_x][y] != "":
                return False, "piece in the way"

    elif mi.abs_dy == 0:
        step = 1 if mi.d_x > 0 else -1
        for x in range(mi.from_x + step, mi.to_x, step):
            if mi.board.board[x][mi.from_y] != "":
                return False, "piece in the way"
    return True, None


def pseudo_bishop(mi: MoveInformation):
    if mi.abs_dy != mi.abs_dx:
        return False, "bishop can only move diagonal"
    step_x = 1 if mi.d_x > 0 else -1
    step_y = 1 if mi.d_y > 0 else -1
    x, y = mi.from_x + step_x, mi.from_y + step_y
    while x != mi.to_x and y != mi.to_y:
        if mi.board.board[x][y] != "":
            return False, "piece in the way"
        x += step_x
        y += step_y
    return True, None


def pseudo_knight(mi: MoveInformation):
    if (mi.abs_dx, mi.abs_dy) not in [(1, 2), (2, 1)]:
        return False, "illegal knight move"
    return True, None


def pseudo_pawn(mi: MoveInformation):
    direction = -1 if mi.from_square_piece.isupper() else 1
    if mi.to_square_piece != "":  # capture
        if mi.abs_dx == 1 and mi.d_y == direction:
            return True, None
        else:
            return False, "illegal pawn capture"
    else:  # move forward
        if mi.d_x == direction and mi.abs_dy == 0:
            return True, None
        start_row = 6 if mi.from_square_piece.isupper() else 1
        if mi.from_x == start_row and mi.d_x == 2 * direction and mi.d_y == 0:
            return True, None
        return False, "illegal pawn move"
