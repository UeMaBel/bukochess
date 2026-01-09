from app.chess.move_flags import FLAG_NONE, FLAG_PROMO_Q, FLAG_PROMO_B, FLAG_PROMOTION, FLAG_PROMO_R, FLAG_PROMO_N
from app.chess.static import PAWN, ROOK, KNIGHT, BISHOP, QUEEN, KING, WHITE, BLACK

FILES = "abcdefgh"
RANKS = "12345678"


def sq(x: int, y: int) -> int:
    return x * 8 + y


def file_y(sq: int) -> int:
    return sq & 7


def rank_x(sq: int) -> int:
    return sq >> 3


def to_uci(move: tuple[int, int, int]) -> str:
    xy, nxy, flag = move
    sqxy = squaretuple_to_notation((rank_x(xy), file_y(xy)))
    sqnxy = squaretuple_to_notation((rank_x(nxy), file_y(nxy)))

    promo = ""
    if flag & FLAG_PROMO_R:
        promo = "r"
    elif flag & FLAG_PROMO_N:
        promo = "n"
    elif flag & FLAG_PROMO_B:
        promo = "b"
    elif flag & FLAG_PROMO_Q:
        promo = "q"

    return sqxy + sqnxy + promo


def from_uci(uci: str) -> int:
    if len(uci) != 2:
        raise ValueError("Invalid UCI")  #
    f_file = ord(uci[0]) - ord("a")
    f_rank = int(uci[1]) - 1
    if f_rank not in (0, 1, 2, 3, 4, 5, 6, 7):
        raise ValueError("Invalid UCI!")
    if f_file not in (0, 1, 2, 3, 4, 5, 6, 7):
        raise ValueError("Invalid UCI!")
    sq = f_rank * 8 + f_file
    return sq


def from_uci_move(uci: str) -> tuple[int, int, int]:
    if len(uci) not in (4, 5):
        raise ValueError("Invalid UCI")

    f_file = ord(uci[0]) - ord("a")
    f_rank = int(uci[1]) - 1
    t_file = ord(uci[2]) - ord("a")
    t_rank = int(uci[3]) - 1

    if f_rank not in (0, 1, 2, 3, 4, 5, 6, 7):
        raise ValueError("Invalid UCI!")
    if f_file not in (0, 1, 2, 3, 4, 5, 6, 7):
        raise ValueError("Invalid UCI!")

    if t_rank not in (0, 1, 2, 3, 4, 5, 6, 7):
        raise ValueError("Invalid UCI!")
    if t_file not in (0, 1, 2, 3, 4, 5, 6, 7):
        raise ValueError("Invalid UCI!")

    from_sq = f_rank * 8 + f_file
    to_sq = t_rank * 8 + t_file

    flags = FLAG_NONE
    if len(uci) == 5:
        promo = uci[4].lower()
        if promo == "q":
            flags |= FLAG_PROMO_Q
        elif promo == "r":
            flags |= FLAG_PROMO_R
        elif promo == "b":
            flags |= FLAG_PROMO_B
        elif promo == "n":
            flags |= FLAG_PROMO_N

    return from_sq, to_sq, flags


def square_to_notation(sq: int) -> str:
    x = rank_x(sq)
    y = file_y(sq)
    return squaretuple_to_notation((x, y))


def squaretuple_to_notation(square: tuple[int, int]) -> str:
    """
    (row, col) -> chess notation
    (0,0) = a8
    (7,7) = h1
    """
    row, col = square
    file = FILES[col]
    rank = RANKS[row]
    return f"{file}{rank}"


def notation_to_int_tuple(notation: str) -> tuple[int, int]:
    file = notation[0].lower()  # 'a'..'h'
    rank = notation[1]  # '1'..'8'

    y = ord(file) - ord("a")
    x = 8 - int(rank)

    return x, y


def int_tuple_to_notation(square: tuple[int, int]) -> str:
    x, y = square
    file = chr(ord("a") + y)
    rank = str(8 - x)
    return file + rank


# Map piece bits to characters
PIECE_TO_CHAR = {
    PAWN: "p",
    KNIGHT: "n",
    BISHOP: "b",
    ROOK: "r",
    QUEEN: "q",
    KING: "k",
}

# Map character to piece bits
CHAR_TO_PIECE = {v: k for k, v in PIECE_TO_CHAR.items()}


def piece_flag_to_str(pf: int) -> str:
    # isolate piece bits (ignore WHITE)
    piece_bits = pf & (PAWN | KNIGHT | BISHOP | ROOK | QUEEN | KING)
    p = PIECE_TO_CHAR.get(piece_bits, "")
    if pf & WHITE:
        p = p.upper()
    return p


def piece_str_to_flag(p: str) -> int:
    flag = WHITE if p.isupper() else BLACK
    p_lower = p.lower()
    flag |= CHAR_TO_PIECE.get(p_lower, 0)
    return flag
