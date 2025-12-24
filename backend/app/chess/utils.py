FILES = "abcdefgh"
RANKS = "12345678"


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
