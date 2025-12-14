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

    def generate_moves(self) -> list[str]:
        # TODO: return list of pseudo-legal moves
        return []

    def make_move(self, move: str):
        # TODO: update board with the move
        pass

    def is_in_check(self, color: str) -> bool:
        # TODO: implement check detection
        return False
