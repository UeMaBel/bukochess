PERFT_CASES = [
    {
        "name": "start_position",
        "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "nodes": {
            1: 20,
            2: 400,
            3: 8902,
            4: 197281,
        },
        "slow_from_depth": 5,
    },
    {
        "name": "kiwipete",
        "fen": "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1",
        "nodes": {
            1: 48,
            2: 2039,
            3: 97862,
        },
        "slow_from_depth": 4,
    },
    {
        "name": "en_passant",
        "fen": "rnbqkbnr/pppp1ppp/8/4p3/3P4/8/PPP1PPPP/RNBQKBNR b KQkq d3 0 2",
        "nodes": {
            1: 29,
            2: 111,
        },
        "slow_from_depth": 3,
    },
]
