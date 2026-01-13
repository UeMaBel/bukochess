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

MAX_DEPTH = 64


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
        self.quiesce_calls = 0
        self.killers = [[None, None] for _ in range(MAX_DEPTH)]

    def choose_move(self, board: Board):
        print(f"searching move with alphabeta. deepness = {self.deepness}")
        gen = MoveGenerator(board)
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
            print(f"Move: {to_uci(m)} | Score: {value}")
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
        print(
            f"nodes: {self.nodes}, cutoffs: {self.cutoffs}, fm_cuttoffs: {self.first_move_cutoffs}, tt: {self.tt_hits}, quiesce {self.quiesce_calls}")

        return m

    def alphabeta(self, gen: MoveGenerator, depth: int, alpha: int, beta: int, maximizing: bool, ply: int) -> int:
        board = gen.board
        alpha_orig = alpha
        beta_orig = beta

        # 1. TT PROBE
        tt_entry = self.tt.get_entry(board.hash)
        if tt_entry is not None and tt_entry.depth >= depth:
            score = self.unscore_mate(tt_entry.score, ply)
            self.tt_hits += 1
            if tt_entry.flag == TT_EXACT:
                return score
            elif tt_entry.flag == TT_LOWER:
                alpha = max(alpha, score)
            elif tt_entry.flag == TT_UPPER:
                beta = min(beta, score)

            if alpha >= beta:
                return alpha if tt_entry.flag == TT_LOWER else beta

        self.nodes += 1
        if depth == 0:
            return self.quiesce(gen, alpha, beta, maximizing)

        moves = gen.legal_moves()
        if not moves:
            if board.is_king_in_check:
                return -MATE_SCORE + ply if maximizing else MATE_SCORE - ply
            return 0

        best_move_from_tt = tt_entry.move if tt_entry else None
        if not best_move_from_tt in moves:
            best_move_from_tt = None

        # --- KILLER MOVE SCORING ---
        scored_moves = []
        for m in moves:
            xy, nxy, flag = m
            score = 0
            if m == best_move_from_tt:
                score = 10000
            elif flag & FLAG_CAPTURE:
                score = 1000 + (PIECE_VALUE_TABLE[gen.board.board[nxy] & 0x07] * 10) - PIECE_VALUE_TABLE[
                    gen.board.board[xy] & 0x07]
            # Check against the two killer slots for this ply
            elif m == self.killers[ply][0]:
                score = 900
            elif m == self.killers[ply][1]:
                score = 800

            scored_moves.append((score, m))

        scored_moves.sort(key=lambda x: x[0], reverse=True)

        best_move = None
        i = -1
        if maximizing:
            value = -float('inf')
            for _, m in scored_moves:  # Iterate over sorted moves
                i += 1
                gen.apply(m)
                score = self.alphabeta(gen, depth - 1, alpha, beta, False, ply + 1)
                gen.undo(m)

                if score > value:
                    value = score
                    best_move = m

                alpha = max(alpha, value)
                if alpha >= beta:
                    # --- RECORD KILLER MOVE ---
                    _, _, flag = m
                    if not (flag & FLAG_CAPTURE):
                        if m != self.killers[ply][0]:
                            self.killers[ply][1] = self.killers[ply][0]
                            self.killers[ply][0] = m

                    self.cutoffs += 1
                    if i == 0: self.first_move_cutoffs += 1
                    break
        else:
            value = float('inf')
            for _, m in scored_moves:  # Iterate over sorted moves
                i += 1
                gen.apply(m)
                score = self.alphabeta(gen, depth - 1, alpha, beta, True, ply + 1)
                gen.undo(m)

                if score < value:
                    value = score
                    best_move = m

                beta = min(beta, value)
                if beta <= alpha:
                    # --- RECORD KILLER MOVE ---
                    _, _, flag = m
                    if not (flag & FLAG_CAPTURE):
                        if m != self.killers[ply][0]:
                            self.killers[ply][1] = self.killers[ply][0]
                            self.killers[ply][0] = m

                    self.cutoffs += 1
                    if i == 0: self.first_move_cutoffs += 1
                    break

        if value <= alpha_orig:
            flag = TT_UPPER
        elif value >= beta_orig:
            flag = TT_LOWER
        else:
            flag = TT_EXACT

        stored_score = self.score_mate(value, ply)
        self.tt.store(board.hash, depth, stored_score, flag, best_move)
        return value

    def quiesce(self, gen: MoveGenerator, alpha, beta, maximizing):
        self.quiesce_calls += 1
        stand_pat = self.evaluate_position(gen.board)

        if maximizing:
            if stand_pat >= beta:
                return beta
            alpha = max(alpha, stand_pat)

            captures = gen.legal_captures()
            scored_captures = []
            for m in captures:
                f, t, _ = m
                score = (PIECE_VALUE_TABLE[gen.board.board[t] & 7] * 10) - PIECE_VALUE_TABLE[gen.board.board[f] & 7]

                if stand_pat + PIECE_VALUE_TABLE[gen.board.board[t] & 7] < alpha:
                    continue
                scored_captures.append((score, m))
            scored_captures.sort(key=lambda x: x[0], reverse=True)

            for _, m in scored_captures:
                gen.apply(m)
                score = self.quiesce(gen, alpha, beta, False)  # Pass False for Black
                gen.undo(m)

                if score >= beta:
                    return beta
                alpha = max(alpha, score)
            return alpha

        else:  # Minimizing (Black)
            if stand_pat <= alpha:
                return alpha
            beta = min(beta, stand_pat)

            captures = gen.legal_captures()
            scored_captures = []
            for m in captures:
                f, t, _ = m
                score = (PIECE_VALUE_TABLE[gen.board.board[t] & 7] * 10) - PIECE_VALUE_TABLE[gen.board.board[f] & 7]
                if stand_pat - PIECE_VALUE_TABLE[gen.board.board[t] & 7] > beta:
                    continue
                scored_captures.append((score, m))
            scored_captures.sort(key=lambda x: x[0], reverse=True)

            for _, m in scored_captures:
                gen.apply(m)
                score = self.quiesce(gen, alpha, beta, True)  # Pass True for White
                gen.undo(m)

                if score <= alpha:
                    return alpha
                beta = min(beta, score)
            return beta

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
