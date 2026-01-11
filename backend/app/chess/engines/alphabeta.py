import random
from app.chess.move_mailbox import MoveMailBoxGenerator as MoveGenerator, BoardMailbox as Board
from app.chess.engines.base import Engine
from app.chess.engines.transposition import TranspositionTable, TT_EXACT, TT_LOWER, TT_UPPER
from app.chess.utils import to_uci
from app.chess.static import WHITE, BLACK
from app.chess.move_flags import FLAG_CAPTURE
from app.chess.static import PIECE_VALUE_TABLE

MATE_SCORE = 100000
MATE_THRESHOLD = 90000


class AlphaBeta(Engine):

    def __init__(self, deepness: int | None = None, seed: int | None = None):
        self._rng = random.Random(seed)
        self.move_value = {}
        if deepness:
            self.deepness = deepness
        else:
            self.deepness = 4
        self.nodes = 0
        self.tt = TranspositionTable()
        self.color = WHITE
        self.nodes = 0
        self.cutoffs = 0
        self.tt_hits = 0
        self.first_move_cutoffs = 0

    def choose_move(self, board: Board):
        print(f"searching move with alphabeta. deepness = {self.deepness}")
        gen = MoveGenerator(board, order=True)
        moves = gen.legal_moves()
        board = gen.board
        self.color = WHITE if board.active_color == WHITE else BLACK
        if not moves:
            return None

        maximizing = board.active_color == WHITE
        best_value = -float("inf") if maximizing else float("inf")
        best_moves = []

        for m in moves:
            gen.apply(m)
            value = self.alphabeta(
                gen,
                self.deepness - 1,
                -float("inf"),
                float("inf"),
                not maximizing, ply=0
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
        m = to_uci(self._rng.choice(best_moves))

        print(f"Best Move: {m} | Score: {best_value}")
        return m

    def alphabeta(self, gen: MoveGenerator, depth: int, alpha: int, beta: int, maximizing: bool, ply: int) -> int:
        self.nodes += 1
        board = gen.board
        alpha_orig = alpha

        # 1. TT PROBE
        tt_entry = self.tt.get_entry(board.hash)
        if tt_entry is not None and tt_entry.depth >= depth:
            score = self.unscore_mate(tt_entry.score, ply)  # ADJUST MATE
            self.tt_hits += 1
            if tt_entry.flag == TT_EXACT:
                return score
            elif tt_entry.flag == TT_LOWER:
                alpha = max(alpha, score)
            elif tt_entry.flag == TT_UPPER:
                beta = min(beta, score)

            if alpha >= beta:
                return score

        if depth == 0:
            return self.evaluate_position(board)

        moves = gen.legal_moves()
        if not moves:
            if board.is_king_in_check:
                return -MATE_SCORE + ply if maximizing else MATE_SCORE - ply
            return 0  # Stalemate

            # We prioritize the move found in the TT first, then captures.
        best_move_from_tt = tt_entry.move if tt_entry else None
        moves.sort(key=lambda m: self.order_moves(m, board, best_move_from_tt), reverse=True)

        best_move = None
        i = -1
        if maximizing:
            value = -float('inf')
            for m in moves:
                i += 1
                gen.apply(m)
                score = self.alphabeta(gen, depth - 1, alpha, beta, False, ply + 1)
                gen.undo(m)

                if score > value:
                    value = score
                    best_move = m

                alpha = max(alpha, value)
                if alpha >= beta:  # Beta Cutoff
                    self.cutoffs += 1
                    if i == 0: self.first_move_cutoffs += 1
                    break
        else:
            value = float('inf')
            for m in moves:
                i += 1
                gen.apply(m)
                score = self.alphabeta(gen, depth - 1, alpha, beta, True, ply + 1)
                gen.undo(m)

                if score < value:
                    value = score
                    best_move = m

                beta = min(beta, value)
                if beta <= alpha:  # Alpha Cutoff
                    self.cutoffs += 1
                    if i == 0: self.first_move_cutoffs += 1
                    break

        # 2. TT STORE
        # Determine flag using the original alpha/beta window
        if value <= alpha_orig:
            flag = TT_UPPER
        elif value >= beta:  # Use the beta passed into function
            flag = TT_LOWER
        else:
            flag = TT_EXACT

        stored_score = self.score_mate(value, ply)  # ADJUST MATE
        self.tt.store(board.hash, depth, stored_score, flag, best_move)
        return value

    def score_mate(self, score, ply):
        if score > MATE_THRESHOLD: return score + ply
        if score < -MATE_THRESHOLD: return score - ply
        return score

    def unscore_mate(self, score, ply):
        if score > MATE_THRESHOLD: return score - ply
        if score < -MATE_THRESHOLD: return score + ply
        return score

    def order_moves(self, move, board, tt_move):
        """
        Assigns a score to a move for sorting.
        High priority: TT move > Captures > Killers > Others.
        """
        # TODO: profile and see if order here or in move_mailbox should stay...or in both
        if move == tt_move:
            return 10000

        from_sq, to_sq, flags = move
        if flags & FLAG_CAPTURE:
            captured_piece = board.board[to_sq]
            moving_piece = board.board[from_sq]
            return 1000 + (PIECE_VALUE_TABLE[captured_piece & 0x07] - PIECE_VALUE_TABLE[moving_piece & 0x07])

        return 0

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

    def evaluate_position(self, board: Board):
        return board.score
