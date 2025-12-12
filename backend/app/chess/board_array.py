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

    def validate_fen(self, fen: str) -> bool:
        fen_split = fen.split(" ")
        if not len(fen_split) == 6:
            return False

        return True

    def from_fen(self, fen: str):
        self.board = []
        cur_row = []
        fen_split = fen.split(" ")

        # fill board
        for c in fen_split[0]:
            if c == "/":
                self.board.append(cur_row)
                cur_row = []
                continue
            if c.isdigit():
                for _ in range(int(c)):
                    cur_row.append("")
            else:
                cur_row.append(c)

        # metadata
        self.active_color = fen_split[1]
        self.castling_rights = fen_split[2]
        self.en_passant = fen_split[3]
        self.halfmove_clock = int(fen_split[4])
        self.fullmove_number = int(fen_split[5])

    def to_fen(self) -> str:
        fen = ""

        # board
        for cur_row in self.board:
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

        # metadata
        fen += " "
        fen += self.active_color
        fen += " "
        fen += self.castling_rights
        fen += " "
        fen += self.en_passant
        fen += " "
        fen += self.halfmove_clock
        fen += " "
        fen += self.fullmove_number

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
