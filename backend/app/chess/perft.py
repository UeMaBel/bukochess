from app.chess.board_array import BoardArray
from app.chess.move_array import MoveGenerator


def perft(board: BoardArray, depth: int) -> int:
    if depth == 0:
        return 1
    nodes = 0
    generator = MoveGenerator(board)
    if depth == 1:
        a = 33
    moves = generator.legal_moves()

    for move in moves:
        undo = move.apply(board)
        nodes += perft(board, depth - 1)
        move.undo(board, undo)

    return nodes


def perft_divide(board: BoardArray, depth: int) -> dict[str, int]:
    if depth < 1:
        raise ValueError("perft_divide depth must be >= 1")

    results: dict[str, int] = {}
    generator = MoveGenerator(board)

    for move in generator.legal_moves():
        undo = move.apply(board)
        nodes = perft(board, depth - 1)
        move.undo(board, undo)

        results[str(move)] = nodes

    return results
