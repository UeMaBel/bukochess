from typing import Optional, Tuple, List, Dict

from app.chess.board_array import BoardArray, Z_CASTLING, Z_EP_FILE, Z_PIECE, Z_SIDE, PIECE_INDEX
from dataclasses import dataclass

from app.chess.utils import notation_to_int_tuple, int_tuple_to_notation, square_to_notation


@dataclass
class MoveUndo:
    captured_piece: str
    captured_square: Tuple[int, int]
    moved_piece: str
    castling_rook_from: Optional[Tuple[int, int]] = None
    castling_rook_to: Optional[Tuple[int, int]] = None
    old_castling: str = "-"
    old_en_passant: str = "-"
    old_halfmove_clock: int = 0
    old_active_color: str = "w"
    repetition_key: Optional[str] = None


class MoveArray:
    """
    Represents a single chess move on a BoardArray.
    """

    def __init__(self, from_square: Tuple[int, int], to_square: Tuple[int, int], promotion: Optional[str] = None,
                 captured_piece: Optional[str] = None):
        """
        :param from_square: tuple (row, col) of starting square, 0-indexed
        :param to_square: tuple (row, col) of target square, 0-indexed
        :param promotion: optional promotion piece ('q', 'r', 'b', 'n')
        """
        self.from_square = from_square
        self.to_square = to_square
        self.promotion = promotion

        # Optional metadata
        self.captured_piece: Optional[str] = captured_piece
        self.castling: Optional[str] = ""
        self.en_passant: bool = False

    def is_capture(self):
        return self.captured_piece != ""

    def is_promotion(self):
        return self.promotion != ""

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

    def is_pseudo_legal(self, board: BoardArray) -> tuple[bool, str | None]:
        mi = MoveInformation(board, self)
        return is_pseudo_legal(mi)

    def apply(self, board: BoardArray) -> MoveUndo:
        from_x, from_y = self.from_square
        to_x, to_y = self.to_square

        from_sq = from_x * 8 + from_y
        to_sq = to_x * 8 + to_y

        piece = board.board[from_x][from_y]
        old_castling = board.castling_rights
        old_castling_mask = board.castling_rights_mask()

        old_en_passant = board.en_passant
        old_halfmove_clock = board.halfmove_clock
        old_active_color = board.active_color

        # Reset halfmove clock for pawn moves or captures
        board.halfmove_clock += 1
        if piece.lower() == "p" or board.board[to_x][to_y] != "":
            board.halfmove_clock = 0

        # Capture (including en-passant)
        if self.en_passant:
            captured_square = (from_x, to_y)
        else:
            captured_square = (to_x, to_y)
        captured_piece = board.board[captured_square[0]][captured_square[1]]
        if self.en_passant:
            board.board[captured_square[0]][captured_square[1]] = ""
        if captured_piece:
            board.hash ^= Z_PIECE[PIECE_INDEX[captured_piece]][to_sq]

        # Move the piece and promotion
        board.board[from_x][from_y] = ""
        board.hash ^= Z_PIECE[PIECE_INDEX[piece]][from_sq]
        board.board[to_x][to_y] = piece

        # Promotion
        moved_piece = piece
        if self.promotion:
            piece_color = "w" if piece.isupper() else "b"
            promotion_piece = self.promotion.upper() if piece_color == "w" else self.promotion.lower()
            board.board[to_x][to_y] = promotion_piece
            moved_piece = promotion_piece
        board.hash ^= Z_PIECE[PIECE_INDEX[moved_piece]][to_sq]

        # Castling
        if piece.lower() == "k" or piece.lower() == "r":
            self.remove_castling_character(board, piece)
        castling_rook_from = castling_rook_to = None
        if self.castling.lower() == "k":  # kingside
            rook_from = (from_x, 7)
            rook_to = (from_x, 5)
            castle_piece = board.board[rook_from[0]][rook_from[1]]
            board.board[rook_to[0]][rook_to[1]] = castle_piece
            board.board[rook_from[0]][rook_from[1]] = ""

            rook_from_sq = from_x * 8 + 7
            rook_to_sq = from_x - 4
            board.hash ^= Z_PIECE[PIECE_INDEX[castle_piece]][rook_from_sq]
            board.hash ^= Z_PIECE[PIECE_INDEX[castle_piece]][rook_to_sq]
            castling_rook_from = rook_from
            castling_rook_to = rook_to
        elif self.castling.lower() == "q":  # queenside
            rook_from = (from_x, 0)
            rook_to = (from_x, 3)
            castle_piece = board.board[rook_from[0]][rook_from[1]]
            board.board[rook_to[0]][rook_to[1]] = board.board[rook_from[0]][rook_from[1]]
            board.board[rook_from[0]][rook_from[1]] = ""
            castling_rook_from = rook_from
            castling_rook_to = rook_to
            rook_from_sq = from_x * 8
            rook_to_sq = rook_from_sq + 3
            board.hash ^= Z_PIECE[PIECE_INDEX[castle_piece]][rook_from_sq]
            board.hash ^= Z_PIECE[PIECE_INDEX[castle_piece]][rook_to_sq]
        new_castling_mask = board.castling_rights_mask()
        board.hash ^= Z_CASTLING[old_castling_mask]
        board.hash ^= Z_CASTLING[new_castling_mask]

        # Update en-passant target
        if board.en_passant != "-":
            file = ord(board.en_passant[0]) - ord("a")
            board.hash ^= Z_EP_FILE[file]
        if piece.lower() == "p" and abs(to_x - from_x) == 2:
            board.en_passant = f"{chr(from_y + ord('a'))}{(from_x + to_x) // 2 + 1}"
            file = ord(board.en_passant[0]) - ord("a")
            board.hash ^= Z_EP_FILE[file]
        else:
            board.en_passant = "-"

        # Switch active color
        board.active_color = "b" if board.active_color == "w" else "w"
        board.hash ^= Z_SIDE

        # Repetition key
        repetition_key = board.create_repetition_key()
        board.position_counts[repetition_key] = board.position_counts.get(repetition_key, 0) + 1

        return MoveUndo(
            captured_piece=captured_piece,
            captured_square=captured_square,
            moved_piece=moved_piece,
            castling_rook_from=castling_rook_from,
            castling_rook_to=castling_rook_to,
            old_castling=old_castling,
            old_en_passant=old_en_passant,
            old_halfmove_clock=old_halfmove_clock,
            old_active_color=old_active_color,
            repetition_key=repetition_key
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
        from_x, from_y = self.from_square
        to_x, to_y = self.to_square

        from_sq = from_x * 8 + from_y
        to_sq = to_x * 8 + to_y

        # remove moved piece
        board.hash ^= Z_PIECE[PIECE_INDEX[board.board[to_x][to_y]]][to_sq]
        board.board[to_x][to_y] = ""
        # Restore moved piece
        if not self.promotion:
            board.board[from_x][from_y] = undo.moved_piece
        else:
            board.board[from_x][from_y] = "p" if undo.old_active_color == "b" else "P"
        piece = board.board[from_x][from_y]
        board.hash ^= Z_PIECE[PIECE_INDEX[piece]][from_sq]

        # Restore captured piece
        cap_x, cap_y = undo.captured_square
        cap_sq = cap_x * 8 + cap_y
        board.board[cap_x][cap_y] = undo.captured_piece
        if undo.captured_piece:
            board.hash ^= Z_PIECE[PIECE_INDEX[undo.captured_piece]][cap_sq]

        # Undo castling rook move
        if undo.castling_rook_from and undo.castling_rook_to:
            rook_piece = board.board[undo.castling_rook_to[0]][undo.castling_rook_to[1]]
            board.board[undo.castling_rook_from[0]][undo.castling_rook_from[1]] = rook_piece
            board.board[undo.castling_rook_to[0]][undo.castling_rook_to[1]] = ""
            rook_from_sq = undo.castling_rook_from[0] * 8 + undo.castling_rook_from[1]
            rook_to_sq = undo.castling_rook_to[0] * 8 + undo.castling_rook_to[1]
            board.hash ^= Z_PIECE[PIECE_INDEX[rook_piece]][rook_from_sq]
            board.hash ^= Z_PIECE[PIECE_INDEX[rook_piece]][rook_to_sq]

        # Restore all other board state
        old_castling_mask = board.castling_rights_mask()
        board.castling_rights = undo.old_castling
        new_castling_mask = board.castling_rights_mask()
        board.hash ^= Z_CASTLING[old_castling_mask]
        board.hash ^= Z_CASTLING[new_castling_mask]
        if board.en_passant != "-":
            file = ord(board.en_passant[0]) - ord("a")
            board.hash ^= Z_EP_FILE[file]
        board.en_passant = undo.old_en_passant
        if board.en_passant != "-":
            file = ord(board.en_passant[0]) - ord("a")
            board.hash ^= Z_EP_FILE[file]
        board.halfmove_clock = undo.old_halfmove_clock
        board.active_color = undo.old_active_color
        board.hash ^= Z_SIDE
        # Revert repetition counter
        board.position_counts[undo.repetition_key] -= 1
        if board.position_counts[undo.repetition_key] == 0:
            del board.position_counts[undo.repetition_key]


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
    _moves_cache: dict[int, list[MoveArray]] = {}

    def __init__(self, board: BoardArray, order: bool = False):
        self._board = board
        self._current_hash: int = board.hash
        self.order = order

    @property
    def board(self) -> BoardArray:
        return self._board

    @board.setter
    def board(self, new_board: BoardArray):
        self._board = new_board
        self._current_hash = new_board.hash

    def legal_moves(self) -> List[MoveArray]:
        """
        Return a list of all legal moves for the current active color.
        """
        if self._current_hash in MoveGenerator._moves_cache:
            return MoveGenerator._moves_cache[self._current_hash]
        pseudo_legal_moves: List[MoveArray] = []
        is_white = self.board.active_color == "w"

        for from_x in range(0, 8):
            for from_y in range(0, 8):
                square = self.board.board[from_x][from_y]
                if square == "":
                    continue
                square_is_upper = square.isupper()
                if is_white != square_is_upper:
                    continue
                for to_x in range(0, 8):
                    for to_y in range(0, 8):
                        cap = self.board.board[to_x][to_y]
                        if cap != "":
                            if cap.isupper() == is_white:
                                continue
                        move = MoveArray(from_square=(from_x, from_y), to_square=(to_x, to_y), captured_piece=cap,
                                         promotion="")
                        mi = MoveInformation(self.board, move)
                        valid, _ = is_pseudo_legal(mi)
                        if valid:
                            # if pawn reaching last rank, generate promotions
                            if square.lower() == "p" and (to_x == 0 or to_x == 7):
                                for promo in ["q", "r", "b", "n"]:
                                    promo_move = MoveArray(from_square=(from_x, from_y),
                                                           to_square=(to_x, to_y),
                                                           promotion=promo)
                                    pseudo_legal_moves.append(promo_move)
                            else:
                                pseudo_legal_moves.append(move)

        # filter out moves that leave own king in check
        color = self.board.active_color
        legal_moves = []
        for move in pseudo_legal_moves:
            king_was_checked = self.board.is_king_in_check(color)
            if king_was_checked and move.castling != "":
                continue
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

        if self.order:
            legal_moves = self.order_moves(legal_moves)
        MoveGenerator._moves_cache[self._current_hash] = legal_moves
        return legal_moves

    def order_moves(self, moves: list[MoveArray]) -> list[MoveArray]:
        promotions = []
        captures = []
        checks = []
        quiet = []

        for move in moves:
            if move.promotion:
                promotions.append(move)
            elif move.is_capture:
                captures.append(move)
            elif self.gives_check(move):
                checks.append(move)
            else:
                quiet.append(move)

        return promotions + captures + checks + quiet

    def gives_check(self, move: MoveArray):
        undo = move.apply(self.board)
        ret = self.board.is_king_in_check()
        move.undo(self.board, undo)
        return ret


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
