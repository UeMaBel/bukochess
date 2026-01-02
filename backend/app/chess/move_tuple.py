from typing import Optional, Tuple, List
from app.chess.static import PAWN_OFFSETS, KING_OFFSETS, KNIGHT_OFFSETS, CASTLE_OFFSETS, ROOK_DIRS, BISHOP_DIRS, \
    QUEEN_DIRS
from app.chess.board_array import BoardArray, Z_CASTLING, Z_EP_FILE, Z_PIECE, Z_SIDE, PIECE_INDEX
from app.chess.move_flags import FLAG_CAPTURE, FLAG_CASTLE_K, FLAG_CASTLE_Q, FLAG_EN_PASSANT, FLAG_NONE, FLAG_PROMO_B, \
    FLAG_PROMO_N, FLAG_PROMO_Q, FLAG_PROMO_R, FLAG_PROMOTION

from app.chess.utils import notation_to_int_tuple, int_tuple_to_notation, square_to_notation, rank_x, file_y, sq


class MoveTupleGenerator:
    """
    Generates all legal moves for a given BoardArray.
    """
    # key= zobist, value= move
    _moves_cache: dict[int, List[tuple[int, int, int]]] = {}

    def __init__(self, board: BoardArray, order: bool = False):
        self._board = board
        self.order = order

    @property
    def board(self) -> BoardArray:
        return self._board

    @board.setter
    def board(self, new_board: BoardArray):
        self._board = new_board

    def legal_moves(self) -> List[tuple[int, int, int]]:
        """
        Return a list of all legal moves for the current active color.
        """
        if self.board.hash in MoveTupleGenerator._moves_cache:
            return MoveTupleGenerator._moves_cache[self.board.hash]

        is_white = self.board.active_color == "w"
        board = self.board.board
        enemy_king = self.board.find_king("b" if is_white else "w")
        board = self.board

        pseudo_legal_moves = self.generate_pseudo_legal_moves(is_white, board.board, enemy_king)
        # filter out moves that leave own king in check
        color = self.board.active_color
        king_was_checked = self.board.is_king_in_check(color)
        legal_moves = []
        for move in pseudo_legal_moves:
            xy, nxy, flags = move
            x = rank_x(xy)
            y = file_y(xy)
            nx = rank_x(nxy)
            ny = file_y(nxy)
            if king_was_checked and ((flags & FLAG_CASTLE_Q) or (flags & FLAG_CASTLE_Q)):
                continue
            self.apply(move)
            if not self.board.is_king_in_check(color):
                if flags & FLAG_CASTLE_K:
                    if self.board.is_square_attacked(color, (x, y + 1)):
                        self.undo(move)
                        continue
                if flags & FLAG_CASTLE_Q:
                    if self.board.is_square_attacked(color, (x, ny + 1)):
                        self.undo(move)
                        continue
                legal_moves.append(move)
            self.undo(move)

        if self.order:
            legal_moves = self.order_moves(legal_moves, self.board)
        MoveTupleGenerator._moves_cache[self.board.hash] = legal_moves
        return legal_moves

    def apply(self, move: Tuple[int, int, int]):
        board = self.board
        from_sq, to_sq, flags = move

        fx, fy = rank_x(from_sq), file_y(from_sq)
        tx, ty = rank_x(to_sq), file_y(to_sq)

        piece = board.board[fx][fy]
        captured_piece = ""
        captured_square = None
        rook_from = rook_to = None

        # --- SAVE OLD STATE ---
        old_castling = board.castling_rights
        old_hash = board.hash

        old_en_passant = board.en_passant
        old_halfmove_clock = board.halfmove_clock
        old_active_color = board.active_color

        # --- REMOVE OLD EP HASH ---
        if board.en_passant != "-":
            f = ord(board.en_passant[0]) - ord("a")
            board.hash ^= Z_EP_FILE[f]

        board.en_passant = "-"

        # --- HALF MOVE CLOCK ---
        board.halfmove_clock += 1
        if piece.lower() == "p":
            board.halfmove_clock = 0

        # --- CAPTURE ---
        if flags & FLAG_EN_PASSANT:
            captured_square = (fx, ty)
        elif flags & FLAG_CAPTURE:
            captured_square = (tx, ty)

        if captured_square:
            cx, cy = captured_square
            captured_piece = board.board[cx][cy]
            board.board[cx][cy] = ""
            board.hash ^= Z_PIECE[PIECE_INDEX[captured_piece]][sq(cx, cy)]
            board.halfmove_clock = 0
        else:
            captured_square = (tx, ty)

        # --- MOVE PIECE ---
        board.board[fx][fy] = ""
        board.hash ^= Z_PIECE[PIECE_INDEX[piece]][from_sq]

        board.board[tx][ty] = piece
        board.hash ^= Z_PIECE[PIECE_INDEX[piece]][to_sq]

        # save new king state
        if piece == "k":
            board.black_king = to_sq
        if piece == "K":
            board.white_king = to_sq

        # --- PROMOTION ---
        if flags & FLAG_PROMOTION:
            board.hash ^= Z_PIECE[PIECE_INDEX[piece]][to_sq]

            piece_color = "w" if piece.isupper() else "b"
            if flags & FLAG_PROMO_N:
                promotion_piece = "n"
            elif flags & FLAG_PROMO_B:
                promotion_piece = "b"
            elif flags & FLAG_PROMO_R:
                promotion_piece = "r"
            else:
                promotion_piece = "q"
            promotion_piece = promotion_piece if piece_color == "b" else promotion_piece.upper()
            board.board[tx][ty] = promotion_piece
            board.hash ^= Z_PIECE[PIECE_INDEX[promotion_piece]][to_sq]

        # --- CASTLING ---
        rook_from = None
        rook_to = None
        if flags & FLAG_CASTLE_K:
            rook_from = (fx, 7)
            rook_to = (fx, 5)
        elif flags & FLAG_CASTLE_Q:
            rook_from = (fx, 0)
            rook_to = (fx, 3)

        if rook_from:
            rf, rt = rook_from, rook_to
            rook = board.board[rf[0]][rf[1]]

            board.board[rf[0]][rf[1]] = ""
            board.board[rt[0]][rt[1]] = rook

            board.hash ^= Z_PIECE[PIECE_INDEX[rook]][sq(*rf)]
            board.hash ^= Z_PIECE[PIECE_INDEX[rook]][sq(*rt)]

        # --- CASTLING RIGHTS ---
        old_mask = board.castling_rights_mask()
        self.remove_castling_character(board, piece, fy)
        new_mask = board.castling_rights_mask()

        if old_mask != new_mask:
            board.hash ^= Z_CASTLING[old_mask]
            board.hash ^= Z_CASTLING[new_mask]

        # --- EN PASSANT CREATION ---
        if flags & FLAG_EN_PASSANT:
            ep_rank = 3 if piece == "P" else 6
            board.en_passant = f"{chr(fy + ord('a'))}{ep_rank}"
            board.hash ^= Z_EP_FILE[fy]

        # --- SIDE TO MOVE ---
        board.active_color = "b" if board.active_color == "w" else "w"
        board.hash ^= Z_SIDE

        # --- REPETITION ---
        board.position_counts[board.hash] = board.position_counts.get(board.hash, 0) + 1

        # save undo info
        board.undo_stack.append((
            captured_piece,  # captured piece ("" if none)
            captured_square,
            piece,
            rook_from,
            rook_to,
            old_castling,
            old_en_passant,
            old_halfmove_clock,
            old_active_color,
            old_hash
        ))

    def apply_old(self, board: BoardArray, move: Tuple[int, int, int]):
        xy, nxy, flags = move

        x = rank_x(xy)
        y = file_y(xy)
        nx = rank_x(nxy)
        ny = file_y(nxy)

        piece = board.board[x][y]
        old_castling = board.castling_rights
        old_castling_mask = board.castling_rights_mask()
        old_hash = board.hash

        old_en_passant = board.en_passant
        old_halfmove_clock = board.halfmove_clock
        old_active_color = board.active_color

        # Reset halfmove clock for pawn moves or captures
        board.halfmove_clock += 1
        if piece.lower() == "p" or board.board[nx][ny] != "":
            board.halfmove_clock = 0

        # Capture (including en-passant)
        if flags & FLAG_CAPTURE:
            captured_square = (nx, ny)
        else:
            captured_square = (x, ny)
        captured_piece = board.board[captured_square[0]][captured_square[1]]
        if flags & FLAG_CAPTURE:
            board.board[captured_square[0]][captured_square[1]] = ""
        if captured_piece:
            csq = sq(captured_square[0], captured_square[1])
            board.hash ^= Z_PIECE[PIECE_INDEX[captured_piece]][csq]
        # Move the piece and promotion
        board.board[x][y] = ""
        board.hash ^= Z_PIECE[PIECE_INDEX[piece]][xy]
        board.board[nx][ny] = piece
        board.hash ^= Z_PIECE[PIECE_INDEX[piece]][nxy]
        # Promotion
        moved_piece = piece
        if flags & FLAG_PROMOTION:
            piece_color = "w" if piece.isupper() else "b"
            if flags & FLAG_PROMO_N:
                promotion_piece = "n"
            elif flags & FLAG_PROMO_B:
                promotion_piece = "b"
            elif flags & FLAG_PROMO_R:
                promotion_piece = "r"
            else:
                promotion_piece = "q"
            promotion_piece = promotion_piece if piece_color == "b" else promotion_piece.upper()
            board.board[nx][ny] = promotion_piece
            moved_piece = promotion_piece
            board.hash ^= Z_PIECE[PIECE_INDEX[moved_piece]][nxy]

        # Castling
        if piece.lower() == "k" or piece.lower() == "r":
            self.remove_castling_character(board, piece, y)
        castling_rook_from = castling_rook_to = None
        if flags & FLAG_CASTLE_K:  # kingside
            rook_from = (x, 7)
            rook_to = (x, 5)
            castle_piece = board.board[rook_from[0]][rook_from[1]]
            board.board[rook_to[0]][rook_to[1]] = castle_piece
            board.board[rook_from[0]][rook_from[1]] = ""

            rook_from_sq = x * 8 + 7
            rook_to_sq = x - 4
            board.hash ^= Z_PIECE[PIECE_INDEX[castle_piece]][rook_from_sq]
            board.hash ^= Z_PIECE[PIECE_INDEX[castle_piece]][rook_to_sq]
            castling_rook_from = rook_from
            castling_rook_to = rook_to
        elif flags & FLAG_CASTLE_Q:  # queenside
            rook_from = (x, 0)
            rook_to = (x, 3)
            castle_piece = board.board[rook_from[0]][rook_from[1]]
            board.board[rook_to[0]][rook_to[1]] = board.board[rook_from[0]][rook_from[1]]
            board.board[rook_from[0]][rook_from[1]] = ""
            castling_rook_from = rook_from
            castling_rook_to = rook_to
            rook_from_sq = x * 8
            rook_to_sq = rook_from_sq + 3
            board.hash ^= Z_PIECE[PIECE_INDEX[castle_piece]][rook_from_sq]
            board.hash ^= Z_PIECE[PIECE_INDEX[castle_piece]][rook_to_sq]
        new_castling_mask = board.castling_rights_mask()
        board.hash ^= Z_CASTLING[old_castling_mask]
        board.hash ^= Z_CASTLING[new_castling_mask]

        # Update en-passant target
        if board.en_passant != "-":
            f = ord(board.en_passant[0]) - ord("a")
            board.hash ^= Z_EP_FILE[f]
        if flags & FLAG_EN_PASSANT:
            x_rank = 3 if "P" else 6
            board.en_passant = f"{chr(y + ord('a'))}{x_rank}"
            f = ord(board.en_passant[0]) - ord("a")
            board.hash ^= Z_EP_FILE[f]
        else:
            board.en_passant = "-"

        # Switch active color
        board.active_color = "b" if board.active_color == "w" else "w"
        board.hash ^= Z_SIDE

        # Repetition key
        repetition_key = board.create_repetition_key()
        board.position_counts[repetition_key] = board.position_counts.get(repetition_key, 0) + 1

        # save undo info
        board.undo_stack.append((
            captured_piece,  # captured piece ("" if none)
            captured_square,
            moved_piece,
            castling_rook_from,
            castling_rook_to,
            old_castling,
            old_en_passant,
            old_halfmove_clock,
            old_active_color,
            repetition_key,
            old_hash
        ))

    def remove_castling_character(self, board: BoardArray, piece: str, y: int):
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
            if y == 7:
                board.castling_rights = board.castling_rights.replace("K", "")
            if y == 0:
                board.castling_rights = board.castling_rights.replace("Q", "")
        elif piece == "r":  # Black rook moved
            if y == 7:
                board.castling_rights = board.castling_rights.replace("k", "")
            if y == 0:
                board.castling_rights = board.castling_rights.replace("q", "")

        if board.castling_rights == "" or board.castling_rights == " ":
            board.castling_rights = board.castling_rights = "-"  # no castling rights left

    def undo(self, move: Tuple[int, int, int]):
        board = self.board
        xy, nxy, flags = move

        x = rank_x(xy)
        y = file_y(xy)
        nx = rank_x(nxy)
        ny = file_y(nxy)

        (
            captured_piece,  # captured piece ("" if none)
            captured_square,
            moved_piece,
            castling_rook_from,
            castling_rook_to,
            old_castling,
            old_en_passant,
            old_halfmove_clock,
            old_active_color,
            old_hash
        ) = board.undo_stack.pop()

        board.hash = old_hash

        # Restore moved piece
        if not flags & FLAG_PROMOTION:
            board.board[x][y] = moved_piece
        else:
            board.board[x][y] = "p" if old_active_color == "b" else "P"
        piece = board.board[x][y]

        # save old king state
        if piece == "k":
            board.black_king = sq(x, y)
        if piece == "K":
            board.white_king = sq(x, y)

        # Restore captured piece
        board.board[nx][ny] = ""
        cap_x, cap_y = captured_square
        cap_sq = cap_x * 8 + cap_y
        # if not flags & FLAG_EN_PASSANT:
        board.board[cap_x][cap_y] = captured_piece

        # Undo castling rook move
        if castling_rook_from and castling_rook_to:
            rook_piece = board.board[castling_rook_to[0]][castling_rook_to[1]]
            board.board[castling_rook_from[0]][castling_rook_from[1]] = rook_piece
            board.board[castling_rook_to[0]][castling_rook_to[1]] = ""

        # Restore all other board state
        board.castling_rights = old_castling
        board.en_passant = old_en_passant
        board.halfmove_clock = old_halfmove_clock
        board.active_color = old_active_color
        # Revert repetition counter
        if board.position_counts.get(old_hash):
            board.position_counts[old_hash] -= 1
            if board.position_counts[old_hash] == 0:
                del board.position_counts[old_hash]

    def order_moves(self, moves: list[Tuple[int, int, int]], board: BoardArray) -> list[Tuple[int, int, int]]:

        promotions = []
        captures = []
        checks = []
        quiet = []

        for move in moves:
            xy, nxy, flags = move
            if flags & FLAG_PROMOTION:
                promotions.append(move)
                continue
            elif flags & FLAG_CAPTURE:
                captures.append(move)
                continue
            elif self.gives_check(move):
                checks.append(move)
            else:
                quiet.append(move)

        return promotions + captures + checks + quiet

    def gives_check(self, move: tuple[int, int, int]):
        self.apply(move)
        ret = self.board.is_king_in_check()
        self.undo(move)
        return ret

    def generate_pseudo_legal_moves(self, is_white, board, enemy_king) -> List[tuple[int, int, int]]:
        moves: List[tuple[int, int, int]] = []
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
                            if target == "":
                                moves.append((sq(x, y), sq(nx, ny), FLAG_NONE))
                            elif target.isupper() != is_white:
                                moves.append((sq(x, y), sq(nx, ny), FLAG_CAPTURE))
                elif p == "k":
                    for dx, dy in KING_OFFSETS:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < 8 and 0 <= ny < 8:
                            ex, ey = enemy_king
                            if abs(nx - ex) <= 1 and abs(ny - ey) <= 1:
                                # illegal: kings adjacent
                                continue
                            target = board[nx][ny]
                            if target == "":
                                moves.append((sq(x, y), sq(nx, ny), FLAG_NONE))
                            elif target.isupper() != is_white:
                                moves.append((sq(x, y), sq(nx, ny), FLAG_CAPTURE))
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
                                        moves.append(
                                            (sq(x, y), sq(nx, ny), FLAG_CASTLE_K if dy == 2 else FLAG_CASTLE_Q))
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
                                            moves.append((sq(x, y), sq(nx, ny), FLAG_CAPTURE | FLAG_PROMO_R))
                                            moves.append((sq(x, y), sq(nx, ny), FLAG_CAPTURE | FLAG_PROMO_N))
                                            moves.append((sq(x, y), sq(nx, ny), FLAG_CAPTURE | FLAG_PROMO_B))
                                            moves.append((sq(x, y), sq(nx, ny), FLAG_CAPTURE | FLAG_PROMO_Q))
                                        else:
                                            moves.append((sq(x, y), sq(nx, ny), FLAG_CAPTURE))
                            elif dy == 0 and (abs(dx) == 1 or abs(dx) == 2):
                                if abs(dx) == 2:
                                    if (is_white and x == 6) or (not is_white and x == 1):
                                        bx = 5 if is_white else 2
                                        if board[bx][y] == "":
                                            moves.append((sq(x, y), sq(nx, ny), FLAG_NONE))
                                else:
                                    if is_promo:
                                        moves.append((sq(x, y), sq(nx, ny), FLAG_PROMO_R))
                                        moves.append((sq(x, y), sq(nx, ny), FLAG_PROMO_N))
                                        moves.append((sq(x, y), sq(nx, ny), FLAG_PROMO_B))
                                        moves.append((sq(x, y), sq(nx, ny), FLAG_PROMO_Q))
                                    else:
                                        moves.append((sq(x, y), sq(nx, ny), FLAG_NONE))
                            elif abs(dy) == 1 and abs(dx) == 1:  # check en poissant
                                if self.board.en_passant != "-":
                                    en_passant_pos = notation_to_int_tuple(self.board.en_passant)
                                    ep_target = board[x][ny]
                                    if nx == en_passant_pos[0] and ny == en_passant_pos[1]:
                                        if (ep_target == "P" and not is_white) or (ep_target == "p" and is_white):
                                            moves.append((sq(x, y), sq(nx, ny), FLAG_CAPTURE | FLAG_EN_PASSANT))

                elif p == "r":
                    for dx, dy in ROOK_DIRS:
                        nx, ny = x + dx, y + dy
                        while 0 <= nx < 8 and 0 <= ny < 8:
                            target = board[nx][ny]
                            if target == "":
                                moves.append((sq(x, y), sq(nx, ny), FLAG_NONE))
                            else:
                                if is_white == target.islower():
                                    moves.append((sq(x, y), sq(nx, ny), FLAG_CAPTURE))
                                break
                            nx += dx
                            ny += dy
                elif p == "b":
                    for dx, dy in BISHOP_DIRS:
                        nx, ny = x + dx, y + dy
                        while 0 <= nx < 8 and 0 <= ny < 8:
                            target = board[nx][ny]
                            if target == "":
                                moves.append((sq(x, y), sq(nx, ny), FLAG_NONE))
                            else:
                                if is_white == target.islower():
                                    moves.append((sq(x, y), sq(nx, ny), FLAG_CAPTURE))
                                break
                            nx += dx
                            ny += dy
                elif p == "q":
                    for dx, dy in QUEEN_DIRS:
                        nx, ny = x + dx, y + dy
                        while 0 <= nx < 8 and 0 <= ny < 8:
                            target = board[nx][ny]
                            if target == "":
                                moves.append((sq(x, y), sq(nx, ny), FLAG_NONE))
                            else:
                                if is_white == target.islower():
                                    moves.append((sq(x, y), sq(nx, ny), FLAG_CAPTURE))
                                break
                            nx += dx
                            ny += dy
        return moves
