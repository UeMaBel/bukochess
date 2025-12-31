import random

random.seed(0)

PIECE_INDEX = {
    "P": 0, "N": 1, "B": 2, "R": 3, "Q": 4, "K": 5,
    "p": 6, "n": 7, "b": 8, "r": 9, "q": 10, "k": 11,
}

Z_PIECE = [[random.getrandbits(64) for _ in range(64)] for _ in range(12)]
Z_SIDE = random.getrandbits(64)
Z_CASTLING = [random.getrandbits(64) for _ in range(16)]
Z_EP_FILE = [random.getrandbits(64) for _ in range(8)]
