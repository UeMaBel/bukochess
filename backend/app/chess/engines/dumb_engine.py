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
        self.deepness = 1

    def choose_move(self, board: BoardArray) -> MoveArray | None:
        generator = MoveGenerator(board)
        moves = generator.legal_moves()

        if not moves:
            return None
        tree = {}
        for m in moves:
            cur_board = board.copy()
            undo = m.apply(cur_board)
            tree[m] = self.compute_moves(board)

        score, moves = self.evaluate_tree(tree, board.active_color.lower() == "w")
        tree = {}
        # if theres a lot of possibilities try again with deepness = 0
        moves_second = {}
        for m in moves:
            cur_board = board.copy()
            undo = m.apply(cur_board)
            moves_second[m] = self.evaluate_position(cur_board)
        score, moves = self.evaluate_tree(moves_second, board.active_color.lower() == "w")

        return self._rng.choice(moves)

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

    def compute_moves(self, board: BoardArray, deepness: int = -1):
        if deepness == -1:
            deepness = self.deepness
        generator = MoveGenerator(board)
        moves = generator.legal_moves()

        move_values = {}
        if not moves:
            self.evaluate_position(board)

        for m in moves:
            cur_board = board.copy()
            undo = m.apply(cur_board)
            if deepness == 0:
                move_values[m] = self.evaluate_position(cur_board)
            else:
                move_values[m] = self.compute_moves(cur_board, deepness - 1)

        return move_values

    def evaluate_position(self, board: BoardArray) -> int:
        score = 0

        for p, x, y in board.get_pieces():
            multiplier = -1 if p.islower() else 1
            score += self.PIECE_VALUE[p]
            score += self.BOARD_VALUE[x][y] * multiplier
        return score
