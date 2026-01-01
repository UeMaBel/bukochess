from typing import Optional, Tuple, List, Dict
from app.chess.static import PAWN_OFFSETS, KING_OFFSETS, KNIGHT_OFFSETS, CASTLE_OFFSETS, ROOK_DIRS, BISHOP_DIRS, \
    QUEEN_DIRS
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
            x_rank = 3 if "P" else 6
            board.en_passant = f"{chr(from_y + ord('a'))}{x_rank}"
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
        board = self.board.board
        enemy_king = self.board.find_king("b" if is_white else "w")
        if self.board.to_fen() == '1r2k2r/p1ppqpb1/bn2pnp1/3PN3/Pp2P3/2N2Q1p/1PPBBPPP/R3K2R w KQk - 1 1':
            a = 33
        pseudo_legal_moves = self.generate_pseudo_legal_moves(is_white, board, enemy_king)

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
            legal_moves = self.order_moves(legal_moves, self.board)
        MoveGenerator._moves_cache[self._current_hash] = legal_moves
        return legal_moves

    def calc_range(self, piece: str, from_x: int, from_y: int):
        to_x = []
        to_y = []
        piece = piece.lower()
        if piece == "p":
            to_x.append(from_x - 1)
            to_x.append(from_x + 1)
            to_x.append(from_x - 2)
            to_x.append(from_x + 2)
            to_y.append(from_y - 1)
            to_y.append(from_y + 1)
        elif piece == "k":
            to_x.append(from_x - 1)
            to_x.append(from_x + 1)
            to_y.append(from_y - 1)
            to_y.append(from_y + 1)
            to_y.append(from_y - 2)
            to_y.append(from_y + 2)

    def order_moves(self, moves: list[MoveArray], board: BoardArray) -> list[MoveArray]:
        promotions = []
        captures = []
        checks = []
        quiet = []

        for move in moves:
            if move.promotion:
                promotions.append(move)
            elif board.board[move.to_square[0]][move.to_square[1]] != "":
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

    def generate_pseudo_legal_moves(self, is_white, board, enemy_king) -> List[MoveArray]:
        pseudo_legal_moves: List[MoveArray] = []
        for x in range(0, 8):
            for y in range(0, 8):
                square = self.board.board[x][y]
                if not square:
                    continue
                square_is_upper = square.isupper()
                if is_white != square_is_upper:
                    continue
                p = square.lower()

                if p == "n":
                    for dx, dy in KNIGHT_OFFSETS:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < 8 and 0 <= ny < 8:
                            target = board[nx][ny]
                            if target == "" or target.isupper() != is_white:
                                pseudo_legal_moves.append(MoveArray((x, y), (nx, ny), captured_piece=target))
                elif p == "k":
                    for dx, dy in KING_OFFSETS:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < 8 and 0 <= ny < 8:
                            ex, ey = enemy_king
                            if abs(nx - ex) <= 1 and abs(ny - ey) <= 1:
                                # illegal: kings adjacent
                                continue
                            target = board[nx][ny]
                            if target == "" or target.isupper() != is_white:
                                pseudo_legal_moves.append(MoveArray((x, y), (nx, ny), captured_piece=target))
                    if (is_white and (x, y) == (7, 4)) or (not is_white and (x, y) == (0, 4)):
                        rights = self.board.castling_rights
                        for dx, dy in CASTLE_OFFSETS:
                            if is_white and dy == -2 and "Q" not in rights:
                                continue
                            if is_white and dy == 2 and "K" not in rights:
                                continue
                            if not is_white and dy == -2 and "q" not in rights:
                                continue
                            if not is_white and dy == 2 and "k" not in rights:
                                continue

                            nx, ny = x + dx, y + dy
                            step_y = y + (1 if dy > 0 else -1)
                            if 0 <= ny < 8:
                                ex, ey = enemy_king
                                if abs(nx - ex) <= 1 and abs(ny - ey) <= 1:
                                    # illegal: kings adjacent
                                    continue
                                rook_y = 0 if dy == -2 else 7
                                rook = board[nx][rook_y]
                                if (is_white and rook == "R") or (not is_white and rook == "r"):
                                    # squares between king and destination must be empty
                                    if board[x][step_y] == "" and board[x][ny] == "":
                                        m = MoveArray((x, y), (nx, ny))
                                        m.castling = "k" if dy == 2 else "q"
                                        pseudo_legal_moves.append(m)
                elif p == "p":
                    for dx, dy in PAWN_OFFSETS[self.board.active_color]:
                        nx, ny = x + dx, y + dy
                        is_promo = nx == 7 or nx == 0
                        if 0 <= nx < 8 and 0 <= ny < 8:
                            target = board[nx][ny]
                            if target != "":  # capture
                                if abs(dx) == 1 and abs(dy) == 1:
                                    if (is_white and board[nx][ny].islower()) or (
                                            not is_white and board[nx][ny].isupper()):
                                        if is_promo:
                                            for promo in ["q", "r", "b", "n"]:
                                                promo_move = MoveArray(from_square=(x, y),
                                                                       to_square=(nx, ny),
                                                                       promotion=promo, captured_piece=target)
                                                pseudo_legal_moves.append(promo_move)
                                        else:
                                            pseudo_legal_moves.append(
                                                MoveArray((x, y), (nx, ny), captured_piece=target))
                            elif dy == 0 and (abs(dx) == 1 or abs(dx) == 2):
                                if abs(dx) == 2:
                                    if (is_white and x == 6) or (not is_white and x == 1):
                                        bx = 5 if is_white else 2
                                        if board[bx][y] == "":
                                            m = MoveArray(
                                                (x, y),
                                                (nx, ny),
                                                captured_piece=target)
                                            pseudo_legal_moves.append(m)
                                else:
                                    if is_promo:
                                        for promo in ["q", "r", "b", "n"]:
                                            promo_move = MoveArray(from_square=(x, y),
                                                                   to_square=(nx, ny),
                                                                   promotion=promo, captured_piece=target)
                                            pseudo_legal_moves.append(promo_move)
                                    else:
                                        pseudo_legal_moves.append(MoveArray((x, y), (nx, ny), captured_piece=target))
                            elif abs(dy) == 1 and abs(dx) == 1:  # check en poissant
                                if self.board.en_passant != "-":
                                    en_passant_pos = notation_to_int_tuple(self.board.en_passant)
                                    ep_target = board[x][ny]
                                    if nx == en_passant_pos[0] and ny == en_passant_pos[1]:
                                        if (ep_target == "P" and not is_white) or (ep_target == "p" and is_white):
                                            ep_move = MoveArray(from_square=(x, y),
                                                                to_square=(nx, ny), captured_piece=ep_target)
                                            ep_move.en_passant = True
                                            pseudo_legal_moves.append(ep_move)
                elif p == "r":
                    for dx, dy in ROOK_DIRS:
                        nx, ny = x + dx, y + dy
                        while 0 <= nx < 8 and 0 <= ny < 8:
                            target = board[nx][ny]
                            if target == "":
                                pseudo_legal_moves.append(MoveArray((x, y), (nx, ny)))
                            else:
                                if is_white == target.islower():
                                    pseudo_legal_moves.append(MoveArray((x, y), (nx, ny), captured_piece=target))
                                break
                            nx += dx
                            ny += dy
                elif p == "b":
                    for dx, dy in BISHOP_DIRS:
                        nx, ny = x + dx, y + dy
                        while 0 <= nx < 8 and 0 <= ny < 8:
                            target = board[nx][ny]
                            if target == "":
                                pseudo_legal_moves.append(MoveArray((x, y), (nx, ny)))
                            else:
                                if is_white == target.islower():
                                    pseudo_legal_moves.append(MoveArray((x, y), (nx, ny), captured_piece=target))
                                break
                            nx += dx
                            ny += dy
                elif p == "q":
                    for dx, dy in QUEEN_DIRS:
                        nx, ny = x + dx, y + dy
                        while 0 <= nx < 8 and 0 <= ny < 8:
                            target = board[nx][ny]
                            if target == "":
                                pseudo_legal_moves.append(MoveArray((x, y), (nx, ny)))
                            else:
                                if is_white == target.islower():
                                    pseudo_legal_moves.append(MoveArray((x, y), (nx, ny), captured_piece=target))
                                break
                            nx += dx
                            ny += dy
        return pseudo_legal_moves
