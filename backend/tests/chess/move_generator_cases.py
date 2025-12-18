"""
Shared move-generation test cases.

All FENs here are valid positions unless explicitly noted.
"""
TEST_POSITIONS = {
    "start_position": {
        "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "expected_moves": 20,
        "is_checkmate": None,
        "is_stalemate": None
    },
    "only_kings": {
        "fen": "8/8/8/8/8/8/4K3/2k5 w - - 0 1",
        "expected_moves": 6,
        "is_checkmate": None,
        "is_stalemate": None
    },
    "open_rooks": {
        "fen": "K7/8/8/8/8/8/R6R/4k3 w - - 0 1",
        "expected_moves": None,
        "is_checkmate": None,
        "is_stalemate": None
    },
    "castling_position": {
        "fen": "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1",
        "expected_moves": None,
        "is_checkmate": False,
        "is_stalemate": False
    },
    "is_in_check": {
        "fen": "rnbqk1nr/pppp1ppp/8/4p3/1b1P4/5N2/PPP1PPPP/RNBQKB1R w KQkq - 2 3",
        "expected_moves": 6,
        "is_checkmate": False,
        "is_stalemate": False
    },
    "easy_pin": {
        "fen": "8/3k4/8/b7/8/2P5/3K4/8 w - - 0 1",
        "expected_moves": 7,
        "is_checkmate": None,
        "is_stalemate": None
    },
    "black_easy_moves": {
        "fen": "8/3k4/8/b7/8/2P5/3K4/8 b - - 0 1",
        "expected_moves": 13,
        "is_checkmate": None,
        "is_stalemate": None
    },
    "black_after_en_passant": {
        "fen": "rnbqkb1r/pppp1ppp/4Pn2/8/8/8/PPP1PPPP/RNBQKBNR b KQkq - 0 3",
        "expected_moves": 29,
        "is_checkmate": None,
        "is_stalemate": None
    },
    "white_en_passant": {
        "fen": "rnbqkb1r/pppp1ppp/5n2/3Pp3/8/8/PPP1PPPP/RNBQKBNR w KQkq e6 0 3",
        "expected_moves": 30,
        "is_checkmate": False,
        "is_stalemate": False
    },
    "checkmate_white": {
        "fen": "rnbqkbnr/ppppp2p/8/1B3ppQ/4P3/8/PPPP1PPP/RNB1K1NR b KQkq - 1 3",
        "expected_moves": 0,
        "is_checkmate": True,
        "is_stalemate": False
    },
    "checkmate_black": {
        "fen": "8/5k2/8/8/1n6/8/2q5/2K5 w - - 0 1",
        "expected_moves": 0,
        "is_checkmate": True,
        "is_stalemate": False
    },
    "stalemate": {
        "fen": "8/5k2/8/8/bn6/8/q7/2K5 w - - 0 1",
        "expected_moves": 0,
        "is_checkmate": False,
        "is_stalemate": True
    },
    "no_stalemate": {
        "fen": "8/5k2/8/8/bn6/8/q6P/2K5 w - - 0 1",
        "expected_moves": 2,
        "is_checkmate": False,
        "is_stalemate": False
    }

}
