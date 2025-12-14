VALID_FENS = {
    "start_position": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    "empty_board": "8/8/8/8/8/8/8/8 w - - 0 1",
    "simple_midgame": "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",
    "black_to_move": "8/8/8/8/8/8/8/8 b - - 15 42",
}

INVALID_FENS = {
    "too_few_fields": "8/8/8/8/8/8/8/8 w - - 0",
    "too_many_fields": "8/8/8/8/8/8/8/8 w - - 0 1 extra",
    "invalid_active_color": "8/8/8/8/8/8/8/8 x - - 0 1",
    "invalid_board_rank": "9/8/8/8/8/8/8/8 w - - 0 1",
    "not_enough_ranks": "8/8/8/8/8/8/8 w - - 0 1",
    "invalid_castling": "8/8/8/8/8/8/8/8 w ABC - 0 1",
    "invalid_en_passant": "8/8/8/8/8/8/8/8 w - z9 0 1",
    "negative_halfmove": "8/8/8/8/8/8/8/8 w - - -1 1",
    "zero_fullmove": "8/8/8/8/8/8/8/8 w - - 0 0",
}
