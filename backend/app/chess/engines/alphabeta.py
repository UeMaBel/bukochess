import random
from app.chess.board_array import BoardArray
from app.chess.move_tuple import MoveTupleGenerator
from app.chess.engines.base import Engine
from app.chess.engines.transposition import TranspositionTable, TT_EXACT, TT_LOWER, TT_UPPER, TTEntry


class AlphaBeta(Engine):
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
        self.deepness = 5
        self.nodes = 0
        self.tt = TranspositionTable()

    def choose_move(self, gen: MoveTupleGenerator):
        moves = gen.legal_moves()
        board = gen.board
        if not moves:
            return None

        maximizing = board.active_color == "w"
        best_value = -float("inf") if maximizing else float("inf")
        best_moves = []

        for m in moves:
            gen.apply(m)
            value = self.alphabeta(
                gen,
                self.deepness - 1,
                -float("inf"),
                float("inf"),
                not maximizing
            )
            gen.undo(m)

            if maximizing:
                if value > best_value:
                    best_value = value
                    best_moves = [m]
                elif value == best_value:
                    best_moves.append(m)
            else:
                if value < best_value:
                    best_value = value
                    best_moves = [m]
                elif value == best_value:
                    best_moves.append(m)

        return self._rng.choice(best_moves)

    def alphabeta(self, gen: MoveTupleGenerator, depth: int, alpha: int, beta: int, maximizing: bool) -> int:
        self.nodes += 1
        board = gen.board
        alpha_orig = alpha
        key = board.hash

        # --- TT probe ---
        tt_score = self.tt.probe(key, depth, alpha, beta)
        if tt_score is not None:
            return tt_score

        if depth == 0:
            return self.evaluate_position(board)

        moves = gen.legal_moves()
        if not moves:
            return self.evaluate_position(board)

        best_move = None

        if maximizing:
            value = -10 ** 9
            for m in moves:
                gen.apply(m)
                score = self.alphabeta(gen, depth - 1, alpha, beta, False)
                gen.undo(m)

                if score > value:
                    value = score
                    best_move = m

                alpha = max(alpha, value)
                if alpha >= beta:
                    break
        else:
            value = 10 ** 9
            for m in moves:
                gen.apply(m)
                score = self.alphabeta(gen, depth - 1, alpha, beta, True)
                gen.undo(m)

                if score < value:
                    value = score
                    best_move = m

                beta = min(beta, value)
                if beta <= alpha:
                    break

        # --- TT store ---
        if value <= alpha_orig:
            flag = TT_UPPER
        elif value >= beta:
            flag = TT_LOWER
        else:
            flag = TT_EXACT

        self.tt.store(key, depth, value, flag, best_move)
        return value

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
