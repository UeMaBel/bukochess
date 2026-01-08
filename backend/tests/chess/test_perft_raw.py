import pytest
from app.chess.move_mailbox import BoardMailbox as Board, MoveMailBoxGenerator as MoveGenerator
from app.chess.perft import run_perft, perft_divide
from app.chess.utils import to_uci

PERFT_FILE = "tests/chess/perft_cases_web.epd"
MAX_TEST_DEPTH = 3


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

    board = Board()
    board.from_fen(fen)
    expected_old = -1
    old_hash = board.hash
    gen = MoveGenerator(board)
    for depth, expected in depth_nodes:
        if depth > MAX_TEST_DEPTH:
            pytest.skip(f"Skipping depth {depth}")

        result = run_perft(gen, depth)

        if result != expected and depth != 1:

            print("--------PERFT DIVIDE------------")
            print(f"result: {result} - expected: {expected}")
            print(board.print_board())
            print(f"FEN: {fen}, depth: {depth}, expected: {expected_old}")
            divide = perft_divide(board, depth)
            for move, count in divide.items():
                print(to_uci(move), count)
            assert False

        expected_old = expected

        assert result == expected, (
            f"Perft failed\n"
            f"FEN: {fen}\n"
            f"Depth: {depth}\n"
            f"Expected: {expected}, Got: {result}"
        )
    assert old_hash == board.hash
