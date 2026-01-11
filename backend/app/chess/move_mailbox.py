from typing import List
from app.chess.static import KING_OFFSETS, KNIGHT_OFFSETS, CASTLE_OFFSETS, ROOK_DIRS, BISHOP_DIRS, \
    QUEEN_DIRS
from app.chess.static import PAWN_OFFSETS_MAILBOX as PAWN_OFFSETS
from app.chess.board_mailbox import BoardMailbox, Z_CASTLING, Z_EP_FILE, Z_PIECE, Z_SIDE
from app.chess.move_flags import FLAG_CAPTURE, FLAG_CASTLE_K, FLAG_CASTLE_Q, FLAG_EN_PASSANT, FLAG_NONE, FLAG_PROMO_B, \
    FLAG_PROMO_N, FLAG_PROMO_Q, FLAG_PROMO_R, FLAG_PROMOTION
from app.chess.static import PAWN, ROOK, BISHOP, KNIGHT, QUEEN, KING, WHITE, BLACK, PIECE, COLOR, EMPTY, COMBINED_TABLE, \
    CASTLE_OFFSETS, CASTLING_KEEP_MASK
from app.chess.utils import rank_x, file_y, from_uci_move
from app.chess.zobrist import piece_flag_to_index
from app.chess.utils import to_uci


class MoveMailBoxGenerator:
    """
    Generates all legal moves for a given BoardArray.
    """
    # key= zobist, value= move
    _moves_cache: dict[int, List[tuple[int, int, int]]] = {}

    def __init__(self, board: BoardMailbox, order: bool = False):
        self._board = board
        self.order = order

    @property
    def board(self) -> BoardMailbox:
        return self._board

    @board.setter
    def board(self, new_board: BoardMailbox):
        self._board = new_board

    def legal_moves(self) -> List[tuple[int, int, int]]:
        """
        Return a list of all legal moves for the current active color.
        """
        if self.board.hash in MoveMailBoxGenerator._moves_cache:
            return MoveMailBoxGenerator._moves_cache[self.board.hash]
        board = self.board
        color = board.active_color
        board = self.board.board
        enemy_king = self.board.find_king(WHITE if color == BLACK else BLACK)

        pseudo_legal_moves = self.generate_pseudo_legal_moves(color, enemy_king)

        # filter out moves that leave own king in check
        king_was_checked = self.board.is_king_in_check
        scored_moves = []
        for move in pseudo_legal_moves:
            xy, nxy, flags = move
            if king_was_checked and ((flags & FLAG_CASTLE_Q) or (flags & FLAG_CASTLE_Q)):
                continue
            self.apply(move)
            if not self.board.is_other_king_in_check:
                candidate = self.board.is_king_in_check
                scored_moves.append((move, candidate))
            self.undo(move)

        if self.order:
            scored_moves = self.order_moves(scored_moves)
        legal_moves = [m for m, _ in scored_moves]
        MoveMailBoxGenerator._moves_cache[self.board.hash] = legal_moves
        return legal_moves

    def apply_uci(self, uci: str):
        from_sq, to_sq, flags = from_uci_move(uci)
        piece = self.board.board[from_sq]

        # capture
        if self.board.board[to_sq] != EMPTY:
            flags |= FLAG_CAPTURE

        # en passant
        elif (piece & PAWN) and self.board.en_passant == to_sq:
            flags |= FLAG_CAPTURE | FLAG_EN_PASSANT

        # castling
        if piece & KING and abs((from_sq % 8) - (to_sq % 8)) == 2:
            if to_sq % 8 == 6:
                flags |= FLAG_CASTLE_K
            else:
                flags |= FLAG_CASTLE_Q

        self.apply((from_sq, to_sq, flags))

    @profile
    def apply(self, move: tuple[int, int, int]):
        board_items = self.board
        board = board_items.board
        from_sq, to_sq, flags = move

        piece = board[from_sq]
        captured_piece = EMPTY
        captured_sq = None
        rook_from = rook_to = None

        # --- SAVE OLD STATE ---
        old_castling = board_items.castling_rights
        old_hash = board_items.hash
        old_en_passant = board_items.en_passant
        old_halfmove_clock = board_items.halfmove_clock
        old_active_color = board_items.active_color
        old_score = board_items.score

        hash = old_hash
        score = old_score

        self.board.is_king_in_check = -1
        self.board.is_other_king_in_check = -1

        # --- REMOVE OLD EN PASSANT HASH ---
        if board_items.en_passant != -1:
            hash ^= Z_EP_FILE[board_items.en_passant % 8]
        self.board.en_passant = -1

        # --- HALF MOVE CLOCK ---
        if piece & PAWN:
            self.board.halfmove_clock = 0
        else:
            self.board.halfmove_clock += 1

        # --- CAPTURE ---
        if flags & FLAG_EN_PASSANT:
            captured_sq = (from_sq & ~7) + (to_sq & 7)
        elif flags & FLAG_CAPTURE:
            captured_sq = to_sq

        if captured_sq is not None:
            captured_piece = board[captured_sq]
            board[captured_sq] = EMPTY
            hash ^= Z_PIECE[piece_flag_to_index(captured_piece)][captured_sq]
            score -= COMBINED_TABLE[captured_piece][captured_sq]
            self.board.halfmove_clock = 0

        # --- MOVE PIECE ---
        board[from_sq] = EMPTY
        hash ^= Z_PIECE[piece_flag_to_index(piece)][from_sq]

        board[to_sq] = piece
        hash ^= Z_PIECE[piece_flag_to_index(piece)][to_sq]
        score -= COMBINED_TABLE[piece][from_sq]
        score += COMBINED_TABLE[piece][to_sq]

        # --- UPDATE KING POSITION ---
        if piece & KING:
            if piece & WHITE:
                self.board.white_king = to_sq
            else:
                self.board.black_king = to_sq

        # --- PROMOTION ---
        if flags & FLAG_PROMOTION:
            hash ^= Z_PIECE[piece_flag_to_index(piece)][to_sq]

            if flags & FLAG_PROMO_N:
                promo_piece = KNIGHT | (piece & COLOR)
            elif flags & FLAG_PROMO_B:
                promo_piece = BISHOP | (piece & COLOR)
            elif flags & FLAG_PROMO_R:
                promo_piece = ROOK | (piece & COLOR)
            else:
                promo_piece = QUEEN | (piece & COLOR)

            board[to_sq] = promo_piece
            hash ^= Z_PIECE[piece_flag_to_index(promo_piece)][to_sq]
            score -= COMBINED_TABLE[piece][to_sq]
            score += COMBINED_TABLE[promo_piece][from_sq]

        # --- CASTLING ---
        if flags & FLAG_CASTLE_K:
            rook_from = to_sq // 8 * 8 + 7
            rook_to = to_sq // 8 * 8 + 5
        elif flags & FLAG_CASTLE_Q:
            rook_from = to_sq // 8 * 8
            rook_to = to_sq // 8 * 8 + 3

        if rook_from is not None:
            rook = board[rook_from]
            board[rook_from] = EMPTY
            board[rook_to] = rook
            hash ^= Z_PIECE[piece_flag_to_index(rook)][rook_from]
            hash ^= Z_PIECE[piece_flag_to_index(rook)][rook_to]
            score -= COMBINED_TABLE[rook][rook_from]
            score += COMBINED_TABLE[rook][rook_to]

        # --- CASTLING RIGHTS ---
        new_rights = old_castling & CASTLING_KEEP_MASK[from_sq] & CASTLING_KEEP_MASK[to_sq]

        if old_castling != new_rights:
            # Hash updates are now extremely fast lookups
            hash ^= Z_CASTLING[old_castling]
            hash ^= Z_CASTLING[new_rights]
            self.board.castling_rights = new_rights

        # --- EN PASSANT CREATION ---
        if piece & PAWN:
            if abs(from_sq - to_sq) == 16:
                ep_target = (from_sq + to_sq) // 2
                self.board.en_passant = ep_target
                hash ^= Z_EP_FILE[ep_target % 8]

        # --- SIDE TO MOVE ---
        self.board.active_color ^= WHITE | BLACK
        hash ^= Z_SIDE

        # --- REPETITION COUNT ---
        self.board.position_counts[hash] = self.board.position_counts.get(hash, 0) + 1

        self.board.hash = hash
        self.board.score = score
        # --- SAVE UNDO INFO ---
        self.board.undo_stack.append((
            captured_piece,
            captured_sq,
            piece,
            rook_from,
            rook_to,
            old_castling,
            old_en_passant,
            old_halfmove_clock,
            old_active_color,
            old_hash,
            old_score
        ))

    def undo(self, move: tuple[int, int, int]):
        from_sq, to_sq, flags = move
        board = self.board.board

        # pop undo info
        (
            captured_piece,
            captured_sq,
            moved_piece,
            rook_from,
            rook_to,
            old_castling,
            old_en_passant,
            old_halfmove,
            old_active_color,
            old_hash,
            old_score
        ) = self.board.undo_stack.pop()

        self.board.hash = old_hash
        self.board.score = old_score
        # Restore moved piece
        if flags & FLAG_PROMOTION:
            piece = PAWN | old_active_color
        else:
            piece = moved_piece
        board[from_sq] = piece
        board[to_sq] = 0

        # Restore king position
        if piece & KING:
            if piece & WHITE:
                self.board.white_king = from_sq
            else:
                self.board.black_king = from_sq

        # Restore captured piece
        if captured_sq is not None:
            board[captured_sq] = captured_piece

        # Undo castling rook
        if rook_from is not None and rook_to is not None:
            rook_piece = board[rook_to]
            board[rook_from] = rook_piece
            board[rook_to] = EMPTY

        # Restore metadata
        self.board.castling_rights = old_castling
        self.board.en_passant = old_en_passant
        self.board.halfmove_clock = old_halfmove
        self.board.active_color = old_active_color

        # Revert repetition counter
        if self.board.position_counts.get(old_hash):
            self.board.position_counts[old_hash] -= 1
            if self.board.position_counts[old_hash] == 0:
                del self.board.position_counts[old_hash]

    def order_moves(self, moves: list[tuple[tuple[int, int, int], bool]]) -> list[tuple[tuple[int, int, int], bool]]:
        promotions = []
        captures = []
        checks = []
        quiet = []
        for move, gives_check in moves:
            _, _, flags = move
            if flags & FLAG_PROMOTION:
                promotions.append((move, gives_check))
            elif flags & FLAG_CAPTURE:
                captures.append((move, gives_check))
            elif gives_check:
                checks.append((move, gives_check))
            else:
                quiet.append((move, gives_check))

        return checks + promotions + captures + quiet

    def gives_check(self, move: tuple[int, int, int]):
        self.apply(move)
        ret = self.board.is_king_in_check
        self.undo(move)
        return ret

    def generate_pseudo_legal_moves(self, color: int, enemy_king_sq: int) -> list[tuple[int, int, int]]:
        moves: list[tuple[int, int, int]] = []
        board = self.board.board
        for sq_from in range(64):
            piece = board[sq_from]
            if not piece or (piece & COLOR) != color:
                continue

            ptype = piece & PIECE
            rank, file = divmod(sq_from, 8)
            is_white = color == WHITE

            # --- knight moves ---
            if ptype == KNIGHT:
                for dr, df in KNIGHT_OFFSETS:
                    r, f = rank + dr, file + df
                    if 0 <= r < 8 and 0 <= f < 8:
                        sq_to = r * 8 + f
                        target = board[sq_to]
                        if not target:
                            moves.append((sq_from, sq_to, FLAG_NONE))
                        elif (target & COLOR) != color:
                            moves.append((sq_from, sq_to, FLAG_CAPTURE))

            # --- king moves ---
            elif ptype == KING:
                for dr, df in KING_OFFSETS:
                    r, f = rank + dr, file + df
                    if 0 <= r < 8 and 0 <= f < 8:
                        sq_to = r * 8 + f
                        if abs(r - (enemy_king_sq // 8)) <= 1 and abs(f - (enemy_king_sq % 8)) <= 1:
                            continue  # illegal: kings adjacent
                        target = board[sq_to]
                        if not target:
                            moves.append((sq_from, sq_to, FLAG_NONE))
                        elif (target & COLOR) != color:
                            moves.append((sq_from, sq_to, FLAG_CAPTURE))
                # --- castling ---
                rights = self.board.castling_to_string()
                if is_white and rank == 0 and file == 4:
                    # white kingside
                    if "K" in rights and not board[0 * 8 + 5] and not board[0 * 8 + 6]:
                        if not self.board.is_square_attacked(4 + 0 * 8, BLACK) and \
                                not self.board.is_square_attacked(5 + 0 * 8, BLACK) and \
                                not self.board.is_square_attacked(6 + 0 * 8, BLACK):
                            moves.append((sq_from, 0 * 8 + 6, FLAG_CASTLE_K))
                    # white queenside
                    if "Q" in rights and not board[0 * 8 + 1] and not board[0 * 8 + 2] and not board[0 * 8 + 3]:
                        if not self.board.is_square_attacked(4 + 0 * 8, BLACK) and \
                                not self.board.is_square_attacked(3 + 0 * 8, BLACK) and \
                                not self.board.is_square_attacked(2 + 0 * 8, BLACK):
                            moves.append((sq_from, 0 * 8 + 2, FLAG_CASTLE_Q))

                elif not is_white and rank == 7 and file == 4:
                    # black kingside
                    if "k" in rights and not board[7 * 8 + 5] and not board[7 * 8 + 6]:
                        if not self.board.is_square_attacked(4 + 7 * 8, WHITE) and \
                                not self.board.is_square_attacked(5 + 7 * 8, WHITE) and \
                                not self.board.is_square_attacked(6 + 7 * 8, WHITE):
                            moves.append((sq_from, 7 * 8 + 6, FLAG_CASTLE_K))
                    # black queenside
                    if "q" in rights and not board[7 * 8 + 1] and not board[7 * 8 + 2] and not board[
                        7 * 8 + 3]:
                        if not self.board.is_square_attacked(4 + 7 * 8, WHITE) and \
                                not self.board.is_square_attacked(3 + 7 * 8, WHITE) and \
                                not self.board.is_square_attacked(2 + 7 * 8, WHITE):
                            moves.append((sq_from, 7 * 8 + 2, FLAG_CASTLE_Q))


            # --- pawn moves ---
            elif ptype == PAWN:
                for dr, df in PAWN_OFFSETS[color]:
                    r, f = rank + dr, file + df
                    if not (0 <= r < 8 and 0 <= f < 8):
                        continue

                    sq_to = r * 8 + f
                    target = board[sq_to]
                    is_promo = (is_white and r == 7) or (not is_white and r == 0)

                    # captures
                    if df != 0 and target and (target & COLOR) != color:
                        if is_promo:
                            for promo_flag in (FLAG_PROMO_R, FLAG_PROMO_N, FLAG_PROMO_B, FLAG_PROMO_Q):
                                moves.append((sq_from, sq_to, FLAG_CAPTURE | promo_flag))
                        else:
                            moves.append((sq_from, sq_to, FLAG_CAPTURE))

                    # en passant
                    if self.board.en_passant != -1 and sq_to == self.board.en_passant:
                        moves.append((sq_from, sq_to, FLAG_CAPTURE | FLAG_EN_PASSANT))

                    # single forward
                    elif df == 0 and not target:
                        if is_promo:
                            for promo_flag in (FLAG_PROMO_R, FLAG_PROMO_N, FLAG_PROMO_B, FLAG_PROMO_Q):
                                moves.append((sq_from, sq_to, promo_flag))
                        else:
                            moves.append((sq_from, sq_to, FLAG_NONE))

                        # double forward
                        if (is_white and rank == 1) or (not is_white and rank == 6):
                            r2 = rank + (2 if is_white else -2)
                            sq_to2 = r2 * 8 + file
                            if board[sq_to2] == EMPTY:
                                moves.append((sq_from, sq_to2, FLAG_NONE))


            # --- rook moves ---
            elif ptype == ROOK:
                for dr, df in ROOK_DIRS:
                    r, f = rank + dr, file + df
                    while 0 <= r < 8 and 0 <= f < 8:
                        sq_to = r * 8 + f
                        target = board[sq_to]
                        if not target:
                            moves.append((sq_from, sq_to, FLAG_NONE))
                        else:
                            if (target & COLOR) != color:
                                moves.append((sq_from, sq_to, FLAG_CAPTURE))
                            break
                        r += dr
                        f += df

            # --- bishop moves ---
            elif ptype == BISHOP:
                for dr, df in BISHOP_DIRS:
                    r, f = rank + dr, file + df
                    while 0 <= r < 8 and 0 <= f < 8:
                        sq_to = r * 8 + f
                        target = board[sq_to]
                        if not target:
                            moves.append((sq_from, sq_to, FLAG_NONE))
                        else:
                            if (target & COLOR) != color:
                                moves.append((sq_from, sq_to, FLAG_CAPTURE))
                            break
                        r += dr
                        f += df

            # --- queen moves ---
            elif ptype == QUEEN:
                for dr, df in QUEEN_DIRS:
                    r, f = rank + dr, file + df
                    while 0 <= r < 8 and 0 <= f < 8:
                        sq_to = r * 8 + f
                        target = board[sq_to]
                        if not target:
                            moves.append((sq_from, sq_to, FLAG_NONE))
                        else:
                            if (target & COLOR) != color:
                                moves.append((sq_from, sq_to, FLAG_CAPTURE))
                            break
                        r += dr
                        f += df

        return moves
