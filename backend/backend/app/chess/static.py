# Color bits (shifted above piece bits)
WHITE = 0b01000000  # 64
BLACK = 0b10000000  # 128
COLOR = WHITE | BLACK

# Piece bits (0–5)
PAWN = 0b000001  # 1
KNIGHT = 0b000010  # 2
BISHOP = 0b000100  # 4
ROOK = 0b001000  # 8
QUEEN = 0b010000  # 16
KING = 0b100000  # 32

PAWN_OFFSETS = {
    "w": [(-1, 0), (-2, 0), (-1, -1), (-1, 1)],
    "b": [(1, 0), (2, 0), (1, -1), (1, 1)],
}
PAWN_OFFSETS_MAILBOX = {
    BLACK: [(-1, 0), (-1, -1), (-1, 1)],
    WHITE: [(1, 0), (1, -1), (1, 1)],
}
KNIGHT_OFFSETS = (
    (2, 1), (1, 2), (-1, 2), (-2, 1),
    (-2, -1), (-1, -2), (1, -2), (2, -1),
)

KING_OFFSETS = (
    (1, 0), (1, 1), (0, 1), (-1, 1),
    (-1, 0), (-1, -1), (0, -1), (1, -1),
)
CASTLE_OFFSETS = (
    (0, 2), (0, -2)
)
ROOK_DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))
BISHOP_DIRS = ((1, 1), (1, -1), (-1, 1), (-1, -1))
QUEEN_DIRS = ROOK_DIRS + BISHOP_DIRS

EMPTY = 0

COLOR = WHITE | BLACK
PIECE = PAWN | KNIGHT | BISHOP | ROOK | QUEEN | KING
ROOK_SLIDERS = ROOK | QUEEN  # 0b00101000
BISHOP_SLIDERS = BISHOP | QUEEN  # 0b00010100

# piece type to index (0..5)
PIECE_TO_INDEX = {
    PAWN: 0,
    KNIGHT: 1,
    BISHOP: 2,
    ROOK: 3,
    QUEEN: 4,
    KING: 5,
}

PIECE_VALUE_TABLE = [0] * 256

for color in (WHITE, BLACK):
    PIECE_VALUE_TABLE[color | PAWN] = 100
    PIECE_VALUE_TABLE[color | KNIGHT] = 320
    PIECE_VALUE_TABLE[color | BISHOP] = 330
    PIECE_VALUE_TABLE[color | ROOK] = 500
    PIECE_VALUE_TABLE[color | QUEEN] = 900
    PIECE_VALUE_TABLE[color | KING] = 20000

# Values now increase as we move TOWARD the promotion rank (Rank 8)
PAWN_PST = [
    0, 0, 0, 0, 0, 0, 0, 0,  # Rank 1 (a1-h1)
    5, 10, 10, -20, -20, 10, 10, 5,  # Rank 2
    5, -5, -10, 0, 0, -10, -5, 5,  # Rank 3
    0, 0, 0, 20, 20, 0, 0, 0,  # Rank 4
    5, 5, 10, 25, 25, 10, 5, 5,  # Rank 5
    10, 10, 20, 30, 30, 20, 10, 10,  # Rank 6
    50, 50, 50, 50, 50, 50, 50, 50,  # Rank 7
    0, 0, 0, 0, 0, 0, 0, 0  # Rank 8 (Promotion)
]
KNIGHT_PST = [
    -50, -40, -30, -30, -30, -30, -40, -50,  # Rank 1
    -40, -20, 0, 5, 5, 0, -20, -40,  # Rank 2
    -30, 5, 10, 15, 15, 10, 5, -30,  # Rank 3
    -30, 0, 15, 20, 20, 15, 0, -30,  # Rank 4
    -30, 5, 15, 20, 20, 15, 5, -30,  # Rank 5
    -30, 0, 10, 15, 15, 10, 0, -30,  # Rank 6
    -40, -20, 0, 0, 0, 0, -20, -40,  # Rank 7
    -50, -40, -30, -30, -30, -30, -40, -50  # Rank 8
]

KING_PST = [
    20, 30, 10, 0, 0, 10, 30, 20,  # Rank 1 (Safe corners)
    20, 20, 0, 0, 0, 0, 20, 20,  # Rank 2
    -10, -20, -20, -20, -20, -20, -20, -10,  # Rank 3
    -20, -30, -30, -40, -40, -30, -30, -20,  # Rank 4
    -30, -40, -40, -50, -50, -40, -40, -30,  # Rank 5
    -30, -40, -40, -50, -50, -40, -40, -30,  # Rank 6
    -30, -40, -40, -50, -50, -40, -40, -30,  # Rank 7
    -30, -40, -40, -50, -50, -40, -40, -30  # Rank 8 (Exposed)
]
BISHOP_PST = [
    -20, -10, -10, -10, -10, -10, -10, -20,  # Rank 1
    -10, 5, 0, 0, 0, 0, 5, -10,  # Rank 2
    -10, 10, 10, 10, 10, 10, 10, -10,  # Rank 3
    -10, 0, 10, 10, 10, 10, 0, -10,  # Rank 4
    -10, 5, 5, 10, 10, 5, 5, -10,  # Rank 5
    -10, 0, 5, 10, 10, 5, 0, -10,  # Rank 6
    -10, 0, 0, 0, 0, 0, 0, -10,  # Rank 7
    -20, -10, -10, -10, -10, -10, -10, -20  # Rank 8
]

ROOK_PST = [
    0, 0, 0, 5, 5, 0, 0, 0,  # Rank 1
    5, 10, 10, 10, 10, 10, 10, 5,  # Rank 2
    -5, 0, 0, 0, 0, 0, 0, -5,  # Rank 3
    -5, 0, 0, 0, 0, 0, 0, -5,  # Rank 4
    -5, 0, 0, 0, 0, 0, 0, -5,  # Rank 5
    -5, 0, 0, 0, 0, 0, 0, -5,  # Rank 6
    10, 10, 10, 10, 10, 10, 10, 10,  # Rank 7 (The "Pig on the 7th")
    0, 0, 0, 5, 5, 0, 0, 0  # Rank 8
]

QUEEN_PST = [
    -20, -10, -10, -5, -5, -10, -10, -20,  # Rank 1
    -10, 0, 5, 0, 0, 0, 0, -10,  # Rank 2
    -10, 5, 5, 5, 5, 5, 0, -10,  # Rank 3
    -5, 0, 5, 5, 5, 5, 0, -5,  # Rank 4
    -5, 0, 5, 5, 5, 5, 0, -5,  # Rank 5
    -10, 0, 5, 5, 5, 5, 0, -10,  # Rank 6
    -10, 0, 0, 0, 0, 0, 0, -10,  # Rank 7
    -20, -10, -10, -5, -5, -10, -10, -20  # Rank 8
]


def flip_sq(sq):
    return sq ^ 56


# Initialize a flat list for O(1) access
COMBINED_TABLE = [[0] * 64 for _ in range(256)]


def init_tables():
    # 1. Map piece types to their PSTs
    pst_map = {
        PAWN: PAWN_PST,
        KNIGHT: KNIGHT_PST,
        BISHOP: BISHOP_PST,
        ROOK: ROOK_PST,
        QUEEN: QUEEN_PST,
        KING: KING_PST
    }

    # 2. Base Material Values
    material = {
        PAWN: 100,
        KNIGHT: 320,
        BISHOP: 330,
        ROOK: 500,
        QUEEN: 900,
        KING: 20000
    }

    for p_type, pst in pst_map.items():
        val = material[p_type]
        for sq in range(64):
            white_piece = WHITE | p_type
            COMBINED_TABLE[white_piece][sq] = val + pst[sq]
            black_piece = BLACK | p_type
            COMBINED_TABLE[black_piece][sq] = -(val + pst[sq ^ 56])


# 1 = W_KING_SIDE (K)
# 2 = W_QUEEN_SIDE (Q)
# 4 = B_KING_SIDE (k)
# 8 = B_QUEEN_SIDE (q)

# Initialize with 15 (all rights preserved)
CASTLING_KEEP_MASK = [15] * 64

# --- WHITE RIGHTS ---
CASTLING_KEEP_MASK[4] = 15 ^ 3  # e1: King moves (Removes bits 1 & 2) -> 12
CASTLING_KEEP_MASK[0] = 15 ^ 2  # a1: Rook moves/captured (Removes bit 2) -> 13
CASTLING_KEEP_MASK[7] = 15 ^ 1  # h1: Rook moves/captured (Removes bit 1) -> 14

# --- BLACK RIGHTS ---
CASTLING_KEEP_MASK[60] = 15 ^ 12  # e8: King moves (Removes bits 4 & 8) -> 3
CASTLING_KEEP_MASK[56] = 15 ^ 8  # a8: Rook moves/captured (Removes bit 8) -> 7
CASTLING_KEEP_MASK[63] = 15 ^ 4  # h8: Rook moves/captured (Removes bit 4) -> 11
