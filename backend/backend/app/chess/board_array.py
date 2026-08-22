from typing import List

from app.chess.board_base import BoardBase
from app.chess.static import PAWN_OFFSETS, BISHOP_DIRS, QUEEN_DIRS, ROOK_DIRS, CASTLE_OFFSETS, KNIGHT_OFFSETS, \
    KING_OFFSETS
from app.chess.zobrist import Z_PIECE, Z_SIDE, Z_CASTLING, Z_EP_FILE, PIECE_INDEX
from app.chess.utils import rank_x, file_y, sq, piece_flag_to_str, piece_str_to_flag


class BoardArray(BoardBase):
    """
    Simple 8x8 array board representation.
    """

    def __init__(self):
        self.board: List[List[str]] = [["" for _ in range(8)] for _ in range(8)]
        self.active_color = "w"
        self.castling_rights = "-"
        self.en_passant = "-"
        self.halfmove_clock = 0
        self.fullmove_number = 1
        self.position_counts: dict[int, int]
        self.position_counts = {}
        self.hash = 0
        self.undo_stack: list[tuple] = []
        self.white_king = 0
        self.black_king = 0

    def compute_hash(self):
        h = 0

        for x in range(8):
            for y in range(8):
                piece = self.board[x][y]
                if piece:
                    sq = x * 8 + y
                    h ^= Z_PIECE[PIECE_INDEX[piece]][sq]

        if self.active_color == "b":
            h ^= Z_SIDE

        h ^= Z_CASTLING[self.castling_rights_mask()]

        if self.en_passant != "-":
            file = ord(self.en_passant[0]) - ord("a")
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
        self.active_color = "b" if self.active_color == "w" else "w"

    def create_repetition_key(self):
        repetition_key = self.hash
        return repetition_key

    def is_threefold_repetition(self) -> bool:
        key = self.create_repetition_key()
        return self.position_counts.get(key, 0) >= 3

    def is_insufficient_material(self) -> bool:
        pieces = []

        for x in range(8):
            for y in range(8):
                p = self.board[x][y]
                if p != "":
                    pieces.append((p, (x, y)))

        # Any pawn, rook or queen → mating material exists
        for p, _ in pieces:
            if p.lower() in ("p", "r", "q"):
                return False

        bishops = []
        knights = []

        for p, (x, y) in pieces:
            if p.lower() == "b":
                bishops.append((p, x, y))
            elif p.lower() == "n":
                knights.append(p)
        if len(pieces) == 2 or len(pieces) == 3:
            return True  # K vs K # or minor vs king
        if len(pieces) == 4 and len(bishops) == 2:
            # Square color = (x + y) % 2
            colors = [(x + y) % 2 for _, x, y in bishops]
            return colors[0] == colors[1]
        return False

    def find_king(self, color: str) -> tuple[int, int]:
        sq = 0
        if color == "w":
            sq = self.white_king
        else:
            sq = self.black_king
        return rank_x(sq), file_y(sq)

    def find_king_initial(self, color: str) -> int:
        king = "K" if color == "w" else "k"
        for x in range(8):
            for y in range(8):
                if self.board[x][y] == king:
                    return sq(x, y)
        raise ValueError("King not found")

    def is_king_in_check(self, color="") -> bool:
        if color == "": color = self.active_color
        king_position = self.find_king(color)
        return self.is_square_attacked(color, king_position)

    def has_legal_moves(self, color: str) -> bool:
        from app.chess.move_tuple import MoveTupleGenerator
        if color == "": color = self.active_color
        current_color = self.active_color
        self.active_color = color

        moves = MoveTupleGenerator(self).legal_moves()

        self.active_color = current_color
        return len(moves) > 0

    def is_checkmate(self, color="") -> bool:
        if color == "": color = self.active_color
        return (
                self.is_king_in_check(color)
                and not self.has_legal_moves(color)
        )

    def is_draw(self, color="") -> bool:
        if color == "": color = self.active_color
        # TODO: implement draw
        return self.is_threefold_repetition()

    def is_stalemate(self, color="") -> bool:
        if color == "": color = self.active_color
        return (
                not self.is_king_in_check(color)
                and not self.has_legal_moves(color)
        )

    def is_square_attacked(self, color: str, sq: tuple[int, int]) -> bool:
        board = self.board
        x, y = sq

        attacker_is_white = (color == "b")

        # --- pawn attacks ---
        pawn = "P" if attacker_is_white else "p"
        pawn_dir = 1 if attacker_is_white else -1
        for dy in (-1, 1):
            nx, ny = x + pawn_dir, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8:
                if board[nx][ny] == pawn:
                    return True

        # --- knight attacks ---
        knight = "N" if attacker_is_white else "n"
        for dx, dy in KNIGHT_OFFSETS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8:
                if board[nx][ny] == knight:
                    return True

        # --- king attacks ---
        king = "K" if attacker_is_white else "k"
        for dx, dy in KING_OFFSETS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8:
                if board[nx][ny] == king:
                    return True

        # --- rook / queen rays ---
        for dx, dy in ROOK_DIRS:
            nx, ny = x + dx, y + dy
            while 0 <= nx < 8 and 0 <= ny < 8:
                p = board[nx][ny]
                if p:
                    if p.isupper() == attacker_is_white and p.lower() in ("r", "q"):
                        return True
                    break
                nx += dx
                ny += dy

        # --- bishop / queen rays ---
        for dx, dy in BISHOP_DIRS:
            nx, ny = x + dx, y + dy
            while 0 <= nx < 8 and 0 <= ny < 8:
                p = board[nx][ny]
                if p:
                    if p.isupper() == attacker_is_white and p.lower() in ("b", "q"):
                        return True
                    break
                nx += dx
                ny += dy

        return False

    def is_square_attacked_old(self, color: str, target_square: tuple[int, int]) -> bool:
        """
        Returns True if the square is attacked by the given color.
        Pseudo-legal moves only; ignores checks for own king safety.
        """
        enemy_color = "b" if color == "w" else "w"
        ex, ey = target_square
        b = self.board

        for x in range(8):
            for y in range(8):
                piece = b[x][y]
                if piece == "":
                    continue
                # skip pieces that are not enemy
                if (piece.isupper() and enemy_color == "b") or (piece.islower() and enemy_color == "w"):
                    continue

                p = piece.lower()
                is_white = piece.isupper()

                # Pawn attacks
                if p == "p":
                    # Pawns attack diagonally
                    dx = -1 if is_white else 1
                    for dy in (-1, 1):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < 8 and 0 <= ny < 8 and (nx, ny) == target_square:
                            return True

                # Knight attacks
                elif p == "n":
                    for dx, dy in KNIGHT_OFFSETS:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < 8 and 0 <= ny < 8 and (nx, ny) == target_square:
                            return True

                # King attacks
                elif p == "k":
                    for dx, dy in KING_OFFSETS:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < 8 and 0 <= ny < 8 and (nx, ny) == target_square:
                            return True

                # Sliding pieces: rook, bishop, queen
                else:
                    dirs = []
                    if p == "r":
                        dirs = ROOK_DIRS
                    elif p == "b":
                        dirs = BISHOP_DIRS
                    elif p == "q":
                        dirs = ROOK_DIRS + BISHOP_DIRS

                    for dx, dy in dirs:
                        nx, ny = x + dx, y + dy
                        while 0 <= nx < 8 and 0 <= ny < 8:
                            target = b[nx][ny]
                            if (nx, ny) == target_square:
                                return True
                            if target != "":
                                break  # blocked
                            nx += dx
                            ny += dy

        return False

    def get_game_state(self):
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

    def get_pieces_location(self, color: str) -> List[tuple[int, int]]:
        pieces = []
        is_white = color == "w"
        for x in range(8):
            for y in range(8):
                if self.board[x][y] == "":
                    continue
                if self.board[x][y].isupper() == is_white:
                    pieces.append((x, y))
        return pieces

    def get_pieces(self):
        pieces = []
        for x in range(8):
            for y in range(8):
                if self.board[x][y] == "":
                    continue
                else:
                    pieces.append((self.board[x][y], x, y))
        return pieces

    def from_fen(self, fen: str):
        valid, message = self.validate_fen(fen)
        if not valid:
            raise ValueError(message)
        self.board = []
        cur_row = []
        parts = fen.strip().split(" ")
        board, active, castling, ep, halfmove, fullmove = parts

        # fill board
        cur_row = []
        i = 0
        for c in board:
            if c == "/":
                self.board.append(cur_row)
                cur_row = []
                continue
            if c.isdigit():
                for _ in range(int(c)):
                    cur_row.append("")
            else:
                cur_row.append(c)
                i += 1
        self.board.append(cur_row)

        # metadata
        self.active_color = active
        self.castling_rights = castling
        self.en_passant = ep
        self.halfmove_clock = int(halfmove)
        self.fullmove_number = int(fullmove)

        self.compute_hash()
        self.position_counts[self.hash] = 1

        try:
            self.white_king = self.find_king_initial("w")
            self.black_king = self.find_king_initial("b")
        except:
            self.white_king = 0
            self.black_king = 0
        return True, "FEN Imported"

    def to_fen(self) -> str:
        fen = ""

        # board
        empty_count = 0
        for cur_row in self.board:
            if empty_count != 0:
                fen += str(empty_count)
            if fen != "":
                fen += "/"
            empty_count = 0
            for c in cur_row:
                if c == "":
                    empty_count += 1
                else:
                    if empty_count != 0:
                        fen += str(empty_count)
                        empty_count = 0
                    fen += c
        if empty_count != 0:
            fen += str(empty_count)

        # metadata
        fen += " "
        fen += self.active_color
        fen += " "
        fen += self.castling_rights
        fen += " "
        fen += self.en_passant
        fen += " "
        fen += str(self.halfmove_clock)
        fen += " "
        fen += str(self.fullmove_number)

        return fen

    def print_board(self):
        print()
        print("    A   B   C   D   E   F   G   H")
        print("  +---+---+---+---+---+---+---+---+")

        for row_idx, row in enumerate(self.board):
            rank = 8 - row_idx
            row_str = f"{rank} |"
            for square in row:
                piece = square if square != "" else "."
                row_str += f" {piece} |"
            print(row_str)
            print("  +---+---+---+---+---+---+---+---+")

        print("    A   B   C   D   E   F   G   H")
        print()
