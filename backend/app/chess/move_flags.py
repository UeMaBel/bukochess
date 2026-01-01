# ─────────────────────────────────────────────
# Move flag bitmask
# ─────────────────────────────────────────────
# lower bits = "what kind of move is this"
# higher bits = "extra information"

FLAG_NONE = 0

# --- capture related ---
FLAG_CAPTURE = 1 << 0  # move captures a piece
FLAG_EN_PASSANT = 1 << 1  # en passant capture

# --- special king moves ---
FLAG_CASTLE_K = 1 << 2  # king-side castling
FLAG_CASTLE_Q = 1 << 3  # queen-side castling

# --- promotion (exactly one may be set) ---
FLAG_PROMO_Q = 1 << 4  # promote to queen
FLAG_PROMO_R = 1 << 5  # promote to rook
FLAG_PROMO_B = 1 << 6  # promote to bishop
FLAG_PROMO_N = 1 << 7  # promote to knight

# mask to test "is promotion"
FLAG_PROMOTION = (
        FLAG_PROMO_Q |
        FLAG_PROMO_R |
        FLAG_PROMO_B |
        FLAG_PROMO_N
)
