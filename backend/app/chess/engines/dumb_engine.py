import random
from app.chess.move_mailbox import MoveMailBoxGenerator as MoveGenerator, BoardMailbox as Board
from app.chess.engines.base import Engine
from app.chess.utils import to_uci

from app.chess.static import WHITE, BLACK
from app.chess.utils import piece_flag_to_str
from app.chess.engines.models import EngineResult


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

    def __init__(self, depth: int, seed: int | None = None):
        super().__init__()
        self.engine_name = "Dumb Engine"
        self._rng = random.Random(seed)
        self.seed = seed
        self.depth = depth
        self.move_value = {}

    def choose_move(self, board: Board) -> EngineResult:
        gen = MoveGenerator(board)
        moves = gen.legal_moves()

        if not moves:
            return None

        maximizing = board.active_color == "w"
        best_score = -float("inf") if maximizing else float("inf")
        best_moves = []

        for m in moves:
            undo = gen.apply(m)
            score = self.minimax(board, self.depth - 1, not maximizing)
            gen.undo(m)

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
            self.evaluation = score

        self.played_color = "w" if board.active_color == WHITE else "b"
        result = EngineResult(
            engine_name=self.engine_name,
            move=to_uci(self._rng.choice(best_moves)),
            played_color=self.played_color,
            metadata={
                "seed": self.seed,
                "depth": self.depth
            }
        )
        return result

    def minimax(self, board: Board, depth: int, maximizing: bool) -> int:
        if depth == 0:
            return self.evaluate_position(board)

        gen = MoveGenerator(board)
        moves = gen.legal_moves()

        if not moves:
            return self.evaluate_position(board)

        if maximizing:
            best = -float("inf")
            for m in moves:
                gen.apply(m)
                score = self.minimax(board, depth - 1, False)
                gen.undo(m)
                best = max(best, score)
            return best
        else:
            best = float("inf")
            for m in moves:
                gen.apply(m)
                score = self.minimax(board, depth - 1, True)
                gen.undo(m)
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

    def evaluate_position(self, board: Board) -> int:
        score = 0

        for p, xy in board.get_pieces():
            p = piece_flag_to_str(p)
            x = xy >> 3
            y = xy & 7
            multiplier = -1 if p.islower() else 1
            score += self.PIECE_VALUE[p]
            score += self.BOARD_VALUE[x][y] * multiplier
        return score
