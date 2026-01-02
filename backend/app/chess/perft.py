from app.chess.board_array import BoardArray
from app.chess.move_tuple import MoveTupleGenerator


def perft(gen: MoveTupleGenerator, depth: int) -> int:
    if depth == 0:
        return 1
    nodes = 0
    moves = gen.legal_moves()
    for move in moves:
        gen.apply(move)
        nodes += perft(gen, depth - 1)
        gen.undo(move)

    return nodes


def perft_divide(board: BoardArray, depth: int) -> dict[tuple[int, int, int], int]:
    if depth < 1:
        raise ValueError("perft_divide depth must be >= 1")

    results: dict[tuple[int, int, int], int] = {}
    generator = MoveTupleGenerator(board)

    for move in generator.legal_moves():
        generator.apply(move)
        nodes = perft(generator, depth - 1)
        generator.undo(move)

        results[move] = nodes

    return results
