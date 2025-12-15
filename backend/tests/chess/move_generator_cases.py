"""
Shared move-generation test cases.

All FENs here are valid positions unless explicitly noted.
"""
TEST_POSITIONS = {
    "start_position": {
        "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "expected_moves": 20,  # known chess fact
    },
    "only_kings": {
        "fen": "8/8/8/8/8/8/4K3/2k5 w - - 0 1",
        "expected_moves": 6,
    },
    "open_rooks": {
        "fen": "8/8/8/8/8/8/R6R/4k3 w - - 0 1",
        "expected_moves": None,  # we only measure time here
    },
    "castling_position": {
        "fen": "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1",
        "expected_moves": None,  # depends on castling logic completeness
    },
}
