from app.chess.board_mailbox import BoardMailbox as Board
from app.chess.move_mailbox import MoveMailBoxGenerator as MoveGenerator

import time


def run_perft(gen: MoveGenerator, depth: int):
    print(f"Starting Perft depth {depth}...")

    start_time = time.perf_counter()
    total_nodes = perft(gen, depth)
    end_time = time.perf_counter()

    duration = end_time - start_time
    # Avoid division by zero if duration is 0
    nps = int(total_nodes / duration) if duration > 0 else 0

    print(f"--- Results ---")
    print(f"Depth:      {depth}")
    print(f"Nodes:      {total_nodes}")
    print(f"Time:       {duration:.3f} s")
    print(f"NPS:        {nps:,}")  # Format with commas for readability
    return total_nodes


def perft(gen: MoveGenerator, depth: int) -> int:
    # This remains your core recursive function
    if depth == 0:
        return 1

    nodes = 0
    moves = gen.legal_moves()
    for move in moves:
        gen.apply(move)
        nodes += perft(gen, depth - 1)
        gen.undo(move)
    return nodes


def perft_divide(board: Board, depth: int) -> dict[tuple[int, int, int], int]:
    if depth < 1:
        raise ValueError("perft_divide depth must be >= 1")

    results: dict[tuple[int, int, int], int] = {}
    generator = MoveGenerator(board)

    for move in generator.legal_moves():
        generator.apply(move)
        nodes = perft(generator, depth - 1)
        generator.undo(move)

        results[move] = nodes

    return results
