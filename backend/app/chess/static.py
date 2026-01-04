# Color bits (shifted above piece bits)
WHITE = 0b01000000  # 64
BLACK = 0b10000000  # 128
COLOR = WHITE | BLACK

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

# Piece bits (0–5)
PAWN = 0b000001  # 1
KNIGHT = 0b000010  # 2
BISHOP = 0b000100  # 4
ROOK = 0b001000  # 8
QUEEN = 0b010000  # 16
KING = 0b100000  # 32

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
