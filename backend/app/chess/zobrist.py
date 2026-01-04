import random
from app.chess.static import PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING, BLACK

random.seed(0)

PIECE_INDEX = {
    "P": 0, "N": 1, "B": 2, "R": 3, "Q": 4, "K": 5,
    "p": 6, "n": 7, "b": 8, "r": 9, "q": 10, "k": 11,
}

Z_PIECE = [[random.getrandbits(64) for _ in range(64)] for _ in range(12)]
Z_SIDE = random.getrandbits(64)
Z_CASTLING = [random.getrandbits(64) for _ in range(16)]
Z_EP_FILE = [random.getrandbits(64) for _ in range(8)]


# Map piece flag to index 0..11 for Z_PIECE
def piece_flag_to_index(pf: int) -> int:
    if pf & PAWN:
        base = 0
    elif pf & KNIGHT:
        base = 1
    elif pf & BISHOP:
        base = 2
    elif pf & ROOK:
        base = 3
    elif pf & QUEEN:
        base = 4
    elif pf & KING:
        base = 5
    else:
        raise ValueError(f"Invalid piece flag: {pf}")

    # add 6 if black
    if pf & BLACK:
        base += 6
    return base
