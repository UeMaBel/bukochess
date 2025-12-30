import random
from app.chess.board_array import BoardArray
from app.chess.move_array import MoveArray, MoveGenerator
from app.chess.engines.base import Engine


class DumbEngine(Engine):
    PIECE_VALUE = {
        "p": -100,
        "b": -300,
        "n": -300,
        "r": -500,
        "q": -900,
        "k": -10000,
        "P": 100,
        "B": 300,
        "N": 300,
        "R": 500,
        "Q": 900,
        "K": 10000
    }
    BOARD_VALUE = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 5, 8, 8, 8, 8, 5, 0],
        [0, 8, 10, 10, 10, 10, 8, 0],
        [0, 8, 10, 10, 10, 10, 8, 0],
        [0, 5, 8, 8, 8, 8, 5, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ]

    def __init__(self, seed: int | None = None):
        self._rng = random.Random(seed)
        self.move_value = {}
        self.deepness = 3

    def choose_move(self, board: BoardArray) -> MoveArray | None:
        generator = MoveGenerator(board)
        moves = generator.legal_moves()

        if not moves:
            return None

        maximizing = board.active_color == "w"
        best_score = -float("inf") if maximizing else float("inf")
        best_moves = []

        for m in moves:
            undo = m.apply(board)
            score = self.minimax(board, self.deepness - 1, not maximizing)
            m.undo(board, undo)

            if maximizing:
                if score > best_score:
                    best_score = score
                    best_moves = [m]
                elif score == best_score:
                    best_moves.append(m)
            else:
                if score < best_score:
                    best_score = score
                    best_moves = [m]
                elif score == best_score:
                    best_moves.append(m)

        return self._rng.choice(best_moves)

    def minimax(self, board: BoardArray, depth: int, maximizing: bool) -> int:
        if depth == 0:
            return self.evaluate_position(board)

        generator = MoveGenerator(board)
        moves = generator.legal_moves()

        if not moves:
            return self.evaluate_position(board)

        if maximizing:
            best = -float("inf")
            for m in moves:
                undo = m.apply(board)
                score = self.minimax(board, depth - 1, False)
                m.undo(board, undo)
                best = max(best, score)
            return best
        else:
            best = float("inf")
            for m in moves:
                undo = m.apply(board)
                score = self.minimax(board, depth - 1, True)
                m.undo(board, undo)
                best = min(best, score)
            return best

    def evaluate_tree(self, tree: dict, white_to_move: bool):
        """
        Recursively evaluate a move tree.
        Returns (best_score, best_moves)
        """

        best_score = None
        best_moves = []

        for move, value in tree.items():
            # Leaf node
            if isinstance(value, int):
                score = value
            else:
                # Internal node: recurse and take opponent's best reply
                score, _ = self.evaluate_tree(value, not white_to_move)

            if best_score is None:
                best_score = score
                best_moves = [move]
            else:
                if white_to_move:
                    if score > best_score:
                        best_score = score
                        best_moves = [move]
                    elif score == best_score:
                        best_moves.append(move)
                else:
                    if score < best_score:
                        best_score = score
                        best_moves = [move]
                    elif score == best_score:
                        best_moves.append(move)

        return best_score, best_moves

    def evaluate_position(self, board: BoardArray) -> int:
        score = 0

        for p, x, y in board.get_pieces():
            multiplier = -1 if p.islower() else 1
            score += self.PIECE_VALUE[p]
            score += self.BOARD_VALUE[x][y] * multiplier
        return score
