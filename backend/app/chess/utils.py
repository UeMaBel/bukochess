from app.chess.move_flags import FLAG_NONE, FLAG_PROMO_Q, FLAG_PROMO_B, FLAG_PROMOTION, FLAG_PROMO_R, FLAG_PROMO_N

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
    sqxy = square_to_notation((rank_x(xy), file_y(xy)))
    sqnxy = square_to_notation((rank_x(nxy), file_y(nxy)))

    return sqxy + sqnxy


def from_uci(uci: str) -> tuple[int, int, int]:
    if len(uci) not in (4, 5):
        raise ValueError

    from_sq = notation_to_int_tuple(uci[:2])
    to_sq = notation_to_int_tuple(uci[2:4])
    xy = from_sq[0] * 8 + from_sq[1]
    nxy = to_sq[0] * 8 + to_sq[1]
    promotion = uci[4] if len(uci) == 5 else None
    flag = FLAG_NONE
    if promotion == "q":
        flag = FLAG_PROMO_Q
    if promotion == "b":
        flag = FLAG_PROMO_B
    if promotion == "n":
        flag = FLAG_PROMO_N
    if promotion == "r":
        flag = FLAG_PROMO_R
    if promotion:
        flag = flag | FLAG_PROMOTION
    return xy, nxy, flag


def square_to_notation(square: tuple[int, int]) -> str:
    """
    (row, col) -> chess notation
    (0,0) = a8
    (7,7) = h1
    """
    row, col = square
    file = FILES[col]
    rank = RANKS[7 - row]
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
