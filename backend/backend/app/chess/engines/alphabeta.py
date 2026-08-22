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

    def __init__(self, depth: int | None = None, seed: int | None = None):
        super().__init__()
        self._rng = random.Random(seed)
        self.engine_name = "Alpha Beta Engine"
        self.move_value = {}
        if depth:
            self.depth = depth
        else:
            self.depth = 4
        self.nodes = 0
        self.tt = TranspositionTable()
        self.cutoffs = 0
        self.tt_hits = 0
        self.first_move_cutoffs = 0
        self.quiesce_calls = 0
        self.killers = [[None, None] for _ in range(MAX_DEPTH)]

    def choose_move(self, board: Board):
        print(f"searching move with alphabeta. max deepness = {self.depth}")

        gen = MoveGenerator(board)
        best_move = None
        for depth in range(1, self.depth + 1):
            # reset per-iteration stats if you want
            self.nodes = 0
            self.cutoffs = 0
            self.first_move_cutoffs = 0
            self.tt_hits = 0
            self.quiesce_calls = 0

            value, move = self.search_root(gen, depth, best_move)
            best_move = move

            print(f"depth {depth}: best {to_uci(move)} score {value}")
            print(
                f"nodes: {self.nodes}, cutoffs: {self.cutoffs}, "
                f"fm_cutoffs: {self.first_move_cutoffs}, "
                f"tt: {self.tt_hits}, quiesce {self.quiesce_calls}"
            )
            self.evaluation = value
            self.played_color = "w" if board.active_color == WHITE else "b"
        return to_uci(best_move)

    def search_root(self, gen: MoveGenerator, depth: int, prev_best_move=None):
        board = gen.board

        alpha = -float("inf")
        beta = float("inf")

        best_value = -float("inf") if board.active_color == WHITE else float("inf")
        best_move = None

        moves = gen.legal_moves()

        scored_moves = []
        for m in moves:
            score = 0
            if m == prev_best_move:
                score = 100000  # Search previous iteration's best move
            elif m[2] & FLAG_CAPTURE:
                score = 1000 + (PIECE_VALUE_TABLE[gen.board.board[m[1]] & 0x07] * 10) - PIECE_VALUE_TABLE[
                    gen.board.board[m[0]] & 0x07]
            scored_moves.append((score, m))

        scored_moves.sort(key=lambda x: x[0], reverse=True)

        for _, m in scored_moves:
            gen.apply(m)
            value = self.alphabeta(
                gen,
                depth - 1,
                alpha,
                beta,
                ply=1
            )
            gen.undo(m)

            if board.active_color == WHITE:
                if value > best_value:
                    best_value = value
                    best_move = m
                alpha = max(alpha, best_value)
            else:
                if value < best_value:
                    best_value = value
                    best_move = m
                beta = min(beta, best_value)

        return best_value, best_move

    def alphabeta(self, gen: MoveGenerator, depth: int, alpha: int, beta: int, ply: int) -> int:
        board = gen.board
        alpha_orig = alpha
        beta_orig = beta

        # 1. TT PROBE
        tt_entry = self.tt.get_entry(board.hash)
        if tt_entry is not None and tt_entry.depth >= depth and ply > 0:
            score = self.unscore_mate(tt_entry.score, ply)
            self.tt_hits += 1
            if tt_entry.flag == TT_EXACT:
                return score
            elif tt_entry.flag == TT_LOWER:
                alpha = max(alpha, score)
            elif tt_entry.flag == TT_UPPER:
                beta = min(beta, score)

            if alpha >= beta:
                return score

        self.nodes += 1
        if depth == 0:
            return self.quiesce(gen, alpha, beta)

        moves = gen.legal_moves()
        if not moves:
            if board.is_king_in_check:
                losing = board.active_color == WHITE
                return (-MATE_SCORE + ply) if losing else (MATE_SCORE - ply)
            else:
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
        if board.active_color == WHITE:
            value = -float('inf')
            for _, m in scored_moves:  # Iterate over sorted moves
                i += 1
                gen.apply(m)
                score = self.alphabeta(gen, depth - 1, alpha, beta, ply + 1)
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
                score = self.alphabeta(gen, depth - 1, alpha, beta, ply + 1)
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
        if best_move and depth > 0:
            self.tt.store(board.hash, depth, stored_score, flag, best_move)
        return value

    def quiesce(self, gen: MoveGenerator, alpha, beta):
        self.quiesce_calls += 1
        board = gen.board
        stand_pat = self.evaluate_position(board)

        if board.active_color == WHITE:
            if stand_pat >= beta:
                return beta
            alpha = max(alpha, stand_pat)

            captures = gen.legal_captures()
            scored_captures = []
            for m in captures:
                f, t, _ = m
                score = (PIECE_VALUE_TABLE[board.board[t] & 7] * 10) - PIECE_VALUE_TABLE[board.board[f] & 7]

                if stand_pat + PIECE_VALUE_TABLE[board.board[t] & 7] < alpha:
                    continue
                scored_captures.append((score, m))
            scored_captures.sort(key=lambda x: x[0], reverse=True)

            for _, m in scored_captures:
                gen.apply(m)
                score = self.quiesce(gen, alpha, beta)  # Pass False for Black
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
                score = (PIECE_VALUE_TABLE[board.board[t] & 7] * 10) - PIECE_VALUE_TABLE[board.board[f] & 7]
                if stand_pat - PIECE_VALUE_TABLE[board.board[t] & 7] > beta:
                    continue
                scored_captures.append((score, m))
            scored_captures.sort(key=lambda x: x[0], reverse=True)

            for _, m in scored_captures:
                gen.apply(m)
                score = self.quiesce(gen, alpha, beta)  # Pass True for White
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

    def evaluate_position(self, board: Board):
        return board.score
