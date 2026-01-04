from typing import List

from app.chess.board_base import BoardBase
from app.chess.static import PAWN_OFFSETS, BISHOP_DIRS, QUEEN_DIRS, ROOK_DIRS, CASTLE_OFFSETS, KNIGHT_OFFSETS, \
    KING_OFFSETS
from app.chess.static import PAWN, ROOK, BISHOP, KNIGHT, QUEEN, KING, WHITE, BLACK, PIECE, COLOR, PIECE_TO_INDEX, \
    ROOK_SLIDERS, BISHOP_SLIDERS, EMPTY
from app.chess.zobrist import Z_PIECE, Z_SIDE, Z_CASTLING, Z_EP_FILE, PIECE_INDEX
from app.chess.utils import rank_x, file_y, piece_flag_to_str, piece_str_to_flag


class BoardMailbox(BoardBase):
    """
    Simple 8x8 array board representation.
    """

    def __init__(self):
        # a list with 64 entries
        self.board: List[int] = [EMPTY] * 64
        self.active_color: int = WHITE
        self.castling_rights = "-"
        self.en_passant = 0
        self.halfmove_clock = 0
        self.fullmove_number = 1
        self.position_counts: dict[str, int]
        self.position_counts = {}
        self.hash = 0
        self.undo_stack: list[tuple] = []
        self.white_king = 0
        self.black_king = 0

    def compute_hash(self):
        h = 0
        board = self.board

        for sq in range(64):
            piece = board[sq]
            if piece:
                ptype = piece & PIECE
                color = piece & COLOR
                idx = PIECE_TO_INDEX[ptype] + (0 if color == WHITE else 6)
                h ^= Z_PIECE[idx][sq]

        # side to move
        if self.active_color == BLACK:
            h ^= Z_SIDE

        # castling rights
        h ^= Z_CASTLING[self.castling_rights_mask()]

        # en passant (file only, if any)
        if self.en_passant != -1:
            file = self.en_passant & 7
            h ^= Z_EP_FILE[file]

        self.hash = h

    def castling_rights_mask(self) -> int:
        mask = 0
        if "K" in self.castling_rights: mask |= 1
        if "Q" in self.castling_rights: mask |= 2
        if "k" in self.castling_rights: mask |= 4
        if "q" in self.castling_rights: mask |= 8
        return mask

    def switch_active_color(self):
        self.active_color ^= (WHITE | BLACK)

    def create_repetition_key(self):
        repetition_key = self.hash
        return repetition_key

    def is_threefold_repetition(self) -> bool:
        key = self.create_repetition_key()
        return self.position_counts.get(key, 0) >= 3

    def is_insufficient_material(self) -> bool:
        pieces = []

        for sq in range(64):
            p = self.board[sq]
            if p:
                pieces.append((p, sq))

        # Any pawn, rook or queen → mating material exists
        for p, _ in pieces:
            if p & (PAWN | ROOK | QUEEN):
                return False

        bishops = []
        knights = []

        for p, sq in pieces:
            if p & BISHOP:
                bishops.append((p, sq))
            elif p & KNIGHT:
                knights.append(p)

        if len(pieces) == 2 or len(pieces) == 3:
            return True  # K vs K or minor vs K

        if len(pieces) == 4 and len(bishops) == 2:
            # Square color = (rank + file) % 2
            colors = [(sq // 8 + sq % 8) % 2 for _, sq in bishops]
            return colors[0] == colors[1]

        return False

    def find_king(self, color: int) -> int:
        return self.white_king if color == WHITE else self.black_king

    def find_king_initial(self, color: int) -> int:
        king = color | KING
        board = self.board
        for sq in range(64):
            if board[sq] == king:
                return sq
        raise ValueError("King not found")

    def is_king_in_check(self, color: int = None) -> bool:
        if color is None:
            color = self.active_color
        king_sq = self.white_king if color == WHITE else self.black_king
        return self.is_square_attacked(king_sq, color ^ (WHITE | BLACK))

    def has_legal_moves(self, color: int = None) -> bool:
        from app.chess.move_mailbox import MoveMailBoxGenerator as Movegenerator
        if color is None:
            color = self.active_color

        current_color = self.active_color
        self.active_color = color

        gen = Movegenerator(self)

        moves = gen.legal_moves()

        self.active_color = current_color
        return bool(moves)

    def is_checkmate(self, color: int = None) -> bool:
        if color is None:
            color = self.active_color
        return self.is_king_in_check(color) and not self.has_legal_moves(color)

    def is_draw(self, color: int = None) -> bool:
        if color is None:
            color = self.active_color
        # TODO: implement draw
        return self.is_threefold_repetition()

    def is_stalemate(self, color: int = None) -> bool:
        if color is None:
            color = self.active_color
        return (
                not self.is_king_in_check(color)
                and not self.has_legal_moves(color)
        )

    def is_square_attacked(self, sq: int, attacker_color: int) -> bool:
        board = self.board
        rank, file = divmod(sq, 8)

        # --- pawn attacks ---
        pawn = PAWN | attacker_color
        pawn_dir = 1 if attacker_color == WHITE else -1
        for df in (-1, 1):
            r, f = rank - pawn_dir, file + df
            if 0 <= r < 8 and 0 <= f < 8:
                if board[r * 8 + f] == pawn:
                    return True

        # --- knight attacks ---
        for dr, df in KNIGHT_OFFSETS:
            r, f = rank + dr, file + df
            if 0 <= r < 8 and 0 <= f < 8:
                if board[r * 8 + f] == (KNIGHT | attacker_color):
                    return True

        # --- king attacks ---
        for dr, df in KING_OFFSETS:
            r, f = rank + dr, file + df
            if 0 <= r < 8 and 0 <= f < 8:
                if board[r * 8 + f] == (KING | attacker_color):
                    return True

        # --- rook / queen rays ---
        for dr, df in ROOK_DIRS:
            r, f = rank + dr, file + df
            while 0 <= r < 8 and 0 <= f < 8:
                p = board[r * 8 + f]
                if p:
                    if (p & COLOR) == attacker_color and (p & ROOK_SLIDERS):
                        return True
                    break
                r += dr
                f += df

        # --- bishop / queen rays ---
        for dr, df in BISHOP_DIRS:
            r, f = rank + dr, file + df
            while 0 <= r < 8 and 0 <= f < 8:
                p = board[r * 8 + f]
                if p:
                    if (p & COLOR) == attacker_color and (p & BISHOP_SLIDERS):
                        return True
                    break
                r += dr
                f += df

        return False

    def get_game_state(self) -> str:
        status = "ok"
        if self.is_stalemate():
            status = "stalemate"
        if self.is_draw():
            status = "draw"
        if self.is_king_in_check():
            status = "check"
        if self.is_checkmate():
            status = "checkmate"
        return status

    def get_pieces_location(self, color: int) -> list[int]:
        pieces = []
        for sq in range(64):
            p = self.board[sq]
            if p and (p & COLOR) == color:
                pieces.append(sq)
        return pieces

    def get_pieces(self) -> list[tuple[int, int]]:
        pieces = []
        for sq in range(64):
            p = self.board[sq]
            if p:
                pieces.append((p, sq))
        return pieces

    def to_2d_board_str(self):
        board2d = [["" for _ in range(8)] for _ in range(8)]
        for sq in range(64):
            rank = 7 - (sq // 8)  # 0 = a8
            file = sq % 8
            board2d[rank][file] = piece_flag_to_str(self.board[sq]) if self.board[sq] else ""
        return board2d

    def print_board(self):
        print()
        print("    A   B   C   D   E   F   G   H")
        print("  +---+---+---+---+---+---+---+---+")

        # rank 8 (top) → rank 1 (bottom)
        for rank in range(7, -1, -1):
            row_str = f"{rank + 1} |"
            for file in range(8):
                sq = rank * 8 + file
                piece = piece_flag_to_str(self.board[sq]) if self.board[sq] else "."
                row_str += f" {piece} |"
            print(row_str)
            print("  +---+---+---+---+---+---+---+---+")

        print("    A   B   C   D   E   F   G   H")
        print()

    def from_fen(self, fen: str):
        """
        Parses FEN into mailbox 64-int board.
        0 = a1 (white bottom-left)
        63 = h8 (black top-right)
        """
        valid, message = self.validate_fen(fen)
        if not valid:
            raise ValueError(message)
        parts = fen.strip().split()
        if len(parts) != 6:
            raise ValueError("Invalid FEN")

        board_fen, active, castling, ep, halfmove, fullmove = parts
        self.board = [EMPTY] * 64

        rank = 7  # FEN starts from rank 8 (top)
        file = 0

        for c in board_fen:
            if c == "/":
                rank -= 1
                file = 0
                continue
            if c.isdigit():
                file += int(c)
            else:
                sq = rank * 8 + file
                self.board[sq] = piece_str_to_flag(c)
                file += 1

        # Active color
        self.active_color = WHITE if active == "w" else BLACK

        # Castling
        self.castling_rights = castling

        # En passant
        if ep == "-":
            self.en_passant = -1
        else:
            ep_file = ord(ep[0]) - ord("a")
            ep_rank = int(ep[1]) - 1  # rank 1 = 0
            self.en_passant = ep_rank * 8 + ep_file

        # Halfmove / fullmove
        self.halfmove_clock = int(halfmove)
        self.fullmove_number = int(fullmove)

        # Update kings
        for sq, pf in enumerate(self.board):
            if pf & KING:
                if pf & WHITE:
                    self.white_king = sq
                else:
                    self.black_king = sq

        self.compute_hash()

        return True, "FEN Imported"

    def to_fen(self) -> str:
        fen_rows = []
        for rank in range(7, -1, -1):
            empty = 0
            row = ""
            for file in range(8):
                sq = rank * 8 + file
                pf = self.board[sq]
                if pf == EMPTY:
                    empty += 1
                else:
                    if empty:
                        row += str(empty)
                        empty = 0
                    row += piece_flag_to_str(pf)
            if empty:
                row += str(empty)
            fen_rows.append(row)
        board_part = "/".join(fen_rows)

        active = "w" if self.active_color == WHITE else "b"
        ep = "-" if self.en_passant == -1 else chr((self.en_passant % 8) + ord("a")) + str((self.en_passant // 8) + 1)

        return f"{board_part} {active} {self.castling_rights} {ep} {self.halfmove_clock} {self.fullmove_number}"
