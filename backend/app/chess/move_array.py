from typing import Optional, Tuple, List, Dict

from app.chess.board_array import BoardArray
from dataclasses import dataclass
from app.chess.utils import notation_to_int_tuple, int_tuple_to_notation, square_to_notation


@dataclass
class MoveUndo:
    captured_piece: str
    active_color: str
    en_passant: str
    promotion: bool
    repetition_key: str
    castling: str
    halfmove_clock: int = 0


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
        self.castling: Optional[str] = ""
        self.en_passant: bool = False

    @staticmethod
    def from_uci(uci: str) -> "MoveArray":
        if len(uci) not in (4, 5):
            raise ValueError

        from_sq = notation_to_int_tuple(uci[:2])
        to_sq = notation_to_int_tuple(uci[2:4])
        promotion = uci[4] if len(uci) == 5 else None

        return MoveArray(from_sq, to_sq, promotion)

    def to_uci(self) -> str:
        """
        UCI-style move notation: e2e4, e7e8q
        """
        from_sq = square_to_notation(self.from_square)
        to_sq = square_to_notation(self.to_square)

        if self.promotion:
            return f"{from_sq}{to_sq}{self.promotion.lower()}"

        return f"{from_sq}{to_sq}"

    def __str__(self) -> str:
        return self.to_uci()

    def is_legal(self, board: BoardArray) -> Tuple[bool, Optional[str]]:
        """
        Validate if the move is legal on the given board.
        Returns (True, None) if legal, (False, reason) if not.
        """
        # TODO: implement piece movement rules, check legality
        return True, None

    def is_pseudo_legal(self, board: BoardArray) -> tuple[bool, str | None]:
        mi = MoveInformation(board, self)
        return is_pseudo_legal(mi)

    def apply(self, board: BoardArray) -> MoveUndo:
        """
        Apply the move to the board (updates BoardArray in-place).
        No validation check here
        """
        old_castling = board.castling_rights
        old_halfmove_clock = board.halfmove_clock
        piece = board.board[self.from_square[0]][self.from_square[1]]
        board.halfmove_clock += 1
        if piece.lower() == "p" or self.captured_piece != "":
            board.halfmove_clock = 0
        if piece.lower() == "k" or piece.lower() == "r":
            self.remove_castling_character(board, piece)

        if piece.lower() == "k":
            # check if castling:
            if self.castling.lower() == "q":
                board.board[self.from_square[0]][0] = ""
                board.board[self.from_square[0]][3] = "r" if piece.islower() else "R"
            elif self.castling.lower() == "k":
                board.board[self.from_square[0]][7] = ""
                board.board[self.from_square[0]][5] = "r" if piece.islower() else "R"
        old_en_passant = board.en_passant
        if not self.en_passant:
            self.captured_piece = board.board[self.to_square[0]][self.to_square[1]]
        else:
            self.captured_piece = board.board[self.from_square[0]][self.to_square[1]]
        active_color = board.active_color
        board.board[self.from_square[0]][self.from_square[1]] = ""
        if self.en_passant:
            board.board[self.from_square[0]][self.to_square[1]] = ""

        # Update en passant target
        if piece.lower() == "p" and abs(self.from_square[0] - self.to_square[0]) == 2:
            # Square pawn passed over
            passed_over_row = (self.from_square[0] + self.to_square[0]) // 2
            passed_over_col = self.from_square[1]
            board.en_passant = int_tuple_to_notation((passed_over_row, passed_over_col))
        else:
            board.en_passant = "-"  # no en passant possible
        promotion_flag = False
        # Promotion logic
        if piece.lower() == "p" and (self.to_square[0] == 0 or self.to_square[0] == 7):
            if self.promotion is None or self.promotion == "":
                promotion_piece = "q" if piece.islower() else "Q"  # default queen
                self.promotion = promotion_piece
            else:
                promotion_piece = self.promotion.upper() if piece.isupper() else self.promotion.lower()
            board.board[self.to_square[0]][self.to_square[1]] = promotion_piece
            promotion_flag = True
        else:
            board.board[self.to_square[0]][self.to_square[1]] = piece

        board.switch_active_color()

        repetition_key = board.create_repetition_key()
        board.position_counts[repetition_key] = board.position_counts.get(repetition_key, 0) + 1

        return MoveUndo(
            captured_piece=self.captured_piece,
            active_color=active_color,
            en_passant=old_en_passant,
            promotion=promotion_flag,
            repetition_key=repetition_key,
            castling=old_castling,
            halfmove_clock=old_halfmove_clock
        )

    def remove_castling_character(self, board: BoardArray, piece: str):
        """
        Remove castling rights for a given piece that moved.
        Returns:
            Updated castling string
        """
        if piece == "K":  # White king moved
            board.castling_rights = board.castling_rights.replace("K", "").replace("Q", "")
        elif piece == "k":  # Black king moved
            board.castling_rights = board.castling_rights.replace("k", "").replace("q", "")
        elif piece == "R":  # White rook moved
            if self.from_square[1] == 7:
                board.castling_rights = board.castling_rights.replace("K", "")
            if self.from_square[1] == 0:
                board.castling_rights = board.castling_rights.replace("Q", "")
        elif piece == "r":  # Black rook moved
            if self.from_square[1] == 7:
                board.castling_rights = board.castling_rights.replace("k", "")
            if self.from_square[1] == 0:
                board.castling_rights = board.castling_rights.replace("q", "")

        if board.castling_rights == "" or board.castling_rights == " ":
            board.castling_rights = board.castling_rights = "-"  # no castling rights left

    def undo(self, board: BoardArray, undo: MoveUndo):
        board.castling_rights = undo.castling
        board.halfmove_clock = undo.halfmove_clock
        piece = board.board[self.to_square[0]][self.to_square[1]]
        if undo.promotion:
            piece = "P" if piece.isupper() else "p"

        board.board[self.to_square[0]][self.to_square[1]] = undo.captured_piece
        board.board[self.from_square[0]][self.from_square[1]] = piece
        board.active_color = undo.active_color
        board.en_passant = undo.en_passant
        board.position_counts[undo.repetition_key] -= 1
        if board.position_counts[undo.repetition_key] == 0:
            del board.position_counts[undo.repetition_key]
        if self.castling.lower() == "q":
            board.board[self.from_square[0]][0] = "r" if piece.islower() else "R"
            board.board[self.from_square[0]][3] = ""
        if self.castling.lower() == "k":
            board.board[self.from_square[0]][5] = ""
            board.board[self.from_square[0]][7] = "r" if piece.islower() else "R"


class MoveInformation:
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


class MoveGenerator:
    """
    Generates all legal moves for a given BoardArray.
    """
    _moves_cache: dict[str, list[MoveArray]] = {}

    def __init__(self, board: BoardArray):
        self._board = board
        self._current_fen: str = board.to_fen()

    @property
    def board(self) -> BoardArray:
        return self._board

    @board.setter
    def board(self, new_board: BoardArray):
        self._board = new_board
        self._current_fen = new_board.to_fen()

    def legal_moves(self) -> List[MoveArray]:
        """
        Return a list of all legal moves for the current active color.
        """
        if self._current_fen in MoveGenerator._moves_cache:
            return MoveGenerator._moves_cache[self._current_fen]

        pseudo_legal_moves: List[MoveArray] = []
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
                        move = MoveArray(from_square=(from_x, from_y), to_square=(to_x, to_y), promotion="")
                        mi = MoveInformation(self.board, move)
                        valid, _ = is_pseudo_legal(mi)
                        if valid:
                            pseudo_legal_moves.append(mi.move)

        # filter out moves that leave own king in check
        color = self.board.active_color
        legal_moves = []
        new_legal_moves = []
        for move in pseudo_legal_moves:
            undo = move.apply(self.board)
            if not self.board.is_king_in_check(color):
                if move.castling != "":  # check if castling was legal
                    if move.castling.lower() == "k":  # kingside castle:
                        if self.board.is_square_attacked(color, (move.from_square[0], move.from_square[1] + 1)):
                            move.undo(self.board, undo)
                            continue
                    if move.castling.lower() == "q":
                        if self.board.is_square_attacked(color, (move.to_square[0], move.to_square[1] + 1)):
                            move.undo(self.board, undo)
                            continue
                legal_moves.append(move)
            move.undo(self.board, undo)
            if undo.promotion:  # create other possibilities then queen promotion

                new_legal_moves.append(
                    MoveArray(from_square=move.from_square, to_square=move.to_square, promotion="b"))
                new_legal_moves.append(
                    MoveArray(from_square=move.from_square, to_square=move.to_square, promotion="n"))
                new_legal_moves.append(
                    MoveArray(from_square=move.from_square, to_square=move.to_square, promotion="r"))
        for move in new_legal_moves:
            undo = move.apply(self.board)
            if not self.board.is_king_in_check(color):
                legal_moves.append(move)

            move.undo(self.board, undo)
        MoveGenerator._moves_cache[self._current_fen] = legal_moves
        return legal_moves


def is_pseudo_legal(mi: "MoveInformation") -> tuple[bool, str | None]:
    """
    Checks if a move is pseudo-legal
    """
    if mi.from_x > 7 or mi.from_y > 7 or mi.to_x > 7 or mi.to_y > 7 or mi.from_x < 0 or mi.from_y < 0 or mi.to_y < 0 or mi.to_x < 0:
        return False, "end of board"
    if mi.abs_dx == 0 and mi.abs_dy == 0:
        return False, "piece didnt move"
    if mi.from_square_piece == "":
        return False, "no piece selected"
    # if mi.active_color == "b" and mi.from_square_piece.isupper():
    #    return False, "blacks turn"
    # if mi.active_color == "w" and not mi.from_square_piece.isupper():
    #    return False, "whites turn"
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
    else:
        return False, "error"


def pseudo_king(mi: "MoveInformation"):
    # check if opponent king is next to to_field
    x_to_check = []
    y_to_check = []
    if mi.abs_dx != 0 and mi.abs_dx != 1 and mi.abs_dx != 2:
        return False, "illegal king move"
    if mi.abs_dy != 0 and mi.abs_dy != 1 and mi.abs_dy != 2:
        return False, "illegal king move"
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
            mi.move.castling = "k"

        # queenside castle
        else:
            if (is_white and "Q" not in rights) or (not is_white and "q" not in rights):
                return False, "no castling rights"

            rook_y = 0
            path = [(mi.from_x, 3), (mi.from_x, 2), (mi.from_x, 1)]
            mi.move.castling = "q"

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


def pseudo_queen(mi: "MoveInformation"):
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


def pseudo_rook(mi: "MoveInformation"):
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


def pseudo_bishop(mi: "MoveInformation"):
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


def pseudo_knight(mi: "MoveInformation"):
    if (mi.abs_dx, mi.abs_dy) not in [(1, 2), (2, 1)]:
        return False, "illegal knight move"
    return True, None


def pseudo_pawn(mi: "MoveInformation"):
    if mi.abs_dy != 0 and mi.abs_dy != 1:
        return False, "illegal pawn move"
    if mi.abs_dx != 1 and mi.abs_dx != 2:
        return False, "illegal pawn move"
    direction = -1 if mi.from_square_piece.isupper() else 1
    if mi.to_square_piece != "":  # capture
        if mi.d_x == direction and mi.abs_dy == 1:
            return True, None
        else:
            return False, "illegal pawn capture"
    else:  # move forward
        if mi.d_x == direction and mi.abs_dy == 0:
            return True, None
        start_row = 6 if mi.from_square_piece.isupper() else 1
        if mi.from_x == start_row and mi.d_x == 2 * direction and mi.d_y == 0:
            if mi.board.board[mi.to_x - direction][mi.to_y] == "":
                return True, None
            else:
                return False, "two-move pawn not possible"
        # en passant logic
        en_passant_row = 3 if mi.from_square_piece.isupper() else 4
        if mi.from_x == en_passant_row:
            if mi.board.en_passant != "-":
                en_passant_pos = notation_to_int_tuple(mi.board.en_passant)
                if mi.to_x == en_passant_pos[0] and mi.to_y == en_passant_pos[1]:
                    mi.move.en_passant = True
                    return True, None
        return False, "illegal pawn move"
