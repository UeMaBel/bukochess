import os
import pytest

from app.chess.board_array import BoardArray
from app.chess.perft import perft
from tests.chess.perft_cases import PERFT_CASES

MAX_PERFT_DEPTH = int(os.getenv("BUKOCHESS_PERFT_DEPTH", "2"))


@pytest.mark.parametrize("case", PERFT_CASES)
def test_perft(case):
    assert True
    board = BoardArray()
    board.from_fen(case["fen"])

    for depth, expected_nodes in case["nodes"].items():
        if depth > MAX_PERFT_DEPTH:
            pytest.skip(f"Skipping depth {depth} (limit={MAX_PERFT_DEPTH})")

        result = perft(board, depth)
        assert result == expected_nodes, (
            f"Perft mismatch in {case['name']} at depth {depth}: "
            f"expected {expected_nodes}, got {result}"
        )
