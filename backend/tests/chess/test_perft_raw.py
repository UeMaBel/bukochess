import pytest

from app.chess.board_array import BoardArray
from app.chess.perft import perft, perft_divide

PERFT_FILE = "tests/chess/perft_cases_web.epd"
MAX_TEST_DEPTH = 2


def parse_perft_line(line: str):
    """
    Parses a line like:
    FEN ;D1 48 ;D2 2039 ;D3 97862
    """
    parts = [p.strip() for p in line.split(";")]
    fen = parts[0]

    depth_nodes = []
    for part in parts[1:]:
        if not part:
            continue
        depth_str, nodes_str = part.split()
        depth = int(depth_str[1:])  # D3 -> 3
        nodes = int(nodes_str)
        depth_nodes.append((depth, nodes))

    return fen, depth_nodes


def load_perft_lines():
    with open(PERFT_FILE, "r", encoding="utf-8") as f:
        return [
            line.strip()
            for line in f
            if line.strip() and not line.startswith("#")
        ]


@pytest.mark.parametrize("line", load_perft_lines())
def test_perft_raw(line):
    fen, depth_nodes = parse_perft_line(line)

    board = BoardArray()
    board.from_fen(fen)
    if fen == "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1":
        a = 33
    expected_old = -1
    for depth, expected in depth_nodes:
        if depth > MAX_TEST_DEPTH:
            pytest.skip(f"Skipping depth {depth}")

        result = perft(board, depth)

        if result != expected and depth != 1:

            print("--------PERFT DIVIDE------------")
            print(f"FEN: {fen}, depth: {depth}, expected: {expected_old}")
            divide = perft_divide(board, depth)
            for move, count in divide.items():
                print(move, count)
            assert False

        expected_old = expected

        assert result == expected, (
            f"Perft failed\n"
            f"FEN: {fen}\n"
            f"Depth: {depth}\n"
            f"Expected: {expected}, Got: {result}"
        )
