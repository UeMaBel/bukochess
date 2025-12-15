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
        "fen": "K7/8/8/8/8/8/R6R/4k3 w - - 0 1",
        "expected_moves": None,  # we only measure time here
    },
    "castling_position": {
        "fen": "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1",
        "expected_moves": None,  # depends on castling logic completeness
    },
    "is_in_check": {
        "fen": "rnbqk1nr/pppp1ppp/8/4p3/1b1P4/5N2/PPP1PPPP/RNBQKB1R w KQkq - 2 3",
        "expected_moves": 6
    },
    "easy_pin": {
        "fen": "8/3k4/8/b7/8/2P5/3K4/8 w - - 0 1",
        "expected_moves": 7
    },
    "black_easy_moves": {
        "fen": "8/3k4/8/b7/8/2P5/3K4/8 b - - 0 1",
        "expected_moves": 13
    },
}
