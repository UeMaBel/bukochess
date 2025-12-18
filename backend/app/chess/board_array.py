from typing import List

from app.chess.board_base import BoardBase


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
        self.position_counts: dict[str, int]
        self.position_counts = {}

    def switch_active_color(self):
        self.active_color = "b" if self.active_color == "w" else "w"

    def create_repetition_key(self):
        repetition_key = self.to_fen().split()[0]
        repetition_key += self.active_color
        repetition_key += self.castling_rights
        repetition_key += self.en_passant
        return repetition_key

    def is_threefold_repetition(self):
        key = self.create_repetition_key()
        return self.position_counts.get(key, 0) >= 3

    def find_king(self, color: str) -> tuple[int, int]:
        king = "K" if color == "w" else "k"
        for x in range(8):
            for y in range(8):
                if self.board[x][y] == king:
                    return x, y
        raise ValueError("King not found")

    def is_king_in_check(self, color: str) -> bool:
        king_position = self.find_king(color)
        return self.is_square_attacked(color, king_position)

    def has_legal_moves(self, color: str) -> bool:
        from app.chess.move_array import MoveGenerator
        current_color = self.active_color
        self.active_color = color

        moves = MoveGenerator(self).legal_moves()

        self.active_color = current_color
        return len(moves) > 0

    def is_checkmate(self, color: str) -> bool:
        return (
                self.is_king_in_check(color)
                and not self.has_legal_moves(color)
        )

    def is_stalemate(self, color: str) -> bool:
        return (
                not self.is_king_in_check(color)
                and not self.has_legal_moves(color)
        )

    def is_square_attacked(self, color: str, position: tuple[int, int]) -> bool:
        opponent_piece_locations = self.get_pieces_location("w" if color == "b" else "b")

        from app.chess.move_array import MoveArray
        for piece_location in opponent_piece_locations:
            move = MoveArray(piece_location, position)
            valid = move.is_pseudo_legal(self)
            if valid[0]:
                return True
        return False

    def get_pieces_location(self, color: str) -> List[tuple[int, int]]:
        pieces = []
        for x in range(8):
            for y in range(8):
                if self.board[x][y] == "":
                    continue
                if self.board[x][y].isupper() and color == "w":
                    pieces.append((x, y))
                elif self.board[x][y].islower() and color == "b":
                    pieces.append((x, y))
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
        self.board.append(cur_row)

        # metadata
        self.active_color = active
        self.castling_rights = castling
        self.en_passant = ep
        self.halfmove_clock = int(halfmove)
        self.fullmove_number = int(fullmove)

        self.position_counts[self.create_repetition_key()] = 1

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
