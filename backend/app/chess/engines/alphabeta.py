import random
from app.chess.move_mailbox import MoveMailBoxGenerator as MoveGenerator, BoardMailbox as Board
from app.chess.engines.base import Engine
from app.chess.engines.transposition import TranspositionTable, TT_EXACT, TT_LOWER, TT_UPPER
from app.chess.engines.tables import PIECE_VALUE_TABLE, BOARD_VALUE_TABLE
from app.chess.utils import to_uci
from app.chess.static import WHITE, BLACK
from app.chess.move_flags import FLAG_CAPTURE


class AlphaBeta(Engine):
    CHECKMATE = 999999

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
        m = to_uci(self._rng.choice(best_moves))

        print(f"Best Move: {m} | Score: {best_value}")
        return m

    def alphabeta(self, gen: MoveGenerator, depth: int, alpha: int, beta: int, maximizing: bool) -> int:
        self.nodes += 1
        board = gen.board
        alpha_orig = alpha

        # tt probe
        tt_entry = self.tt.get_entry(board.hash)
        if tt_entry is not None and tt_entry.depth >= depth:
            if tt_entry.flag == TT_EXACT:
                return tt_entry.score
            elif tt_entry.flag == TT_LOWER:
                alpha = max(alpha, tt_entry.score)
            elif tt_entry.flag == TT_UPPER:
                beta = min(beta, tt_entry.score)

            if alpha >= beta:
                self.tt_hits += 1
                return tt_entry.score

        if depth == 0:
            return self.evaluate_position(board, depth)

        moves = gen.legal_moves()

        # checkmate / stalemate
        if not moves:
            if board.is_king_in_check:  # Checkmate
                return -(self.CHECKMATE + depth) if maximizing else (self.CHECKMATE + depth)
            print("stalemate")
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
                score = self.alphabeta(gen, depth - 1, alpha, beta, False)
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
                score = self.alphabeta(gen, depth - 1, alpha, beta, True)
                gen.undo(m)

                if score < value:
                    value = score
                    best_move = m

                beta = min(beta, value)
                if beta <= alpha:  # Alpha Cutoff
                    self.cutoffs += 1
                    if i == 0: self.first_move_cutoffs += 1
                    break

        if value <= alpha_orig:
            flag = TT_UPPER
        elif value >= beta:
            flag = TT_LOWER
        else:
            flag = TT_EXACT

        self.tt.store(board.hash, depth, value, flag, best_move)
        return value

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

    def alphabeta_old(self, gen: MoveGenerator, depth: int, alpha: int, beta: int, maximizing: bool) -> int:
        self.nodes += 1
        board = gen.board
        alpha_orig = alpha
        beta_orig = beta
        key = board.hash

        # --- TT probe ---
        tt_score = self.tt.probe(key, depth, alpha, beta)
        if tt_score is not None:
            return tt_score

        if depth == 0:
            return self.evaluate_position(board, depth)

        moves = gen.legal_moves()
        if not moves:
            return self.evaluate_position(board, depth)

        best_move = None

        if maximizing:
            value = -10 ** 9
            for m in moves:
                if to_uci(m) == "h4f6":
                    b = 3
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
        elif value >= beta_orig:
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

    def evaluate_position(self, board: Board, depth: int) -> int:
        """
        Returns the static evaluation of the board from White's perspective.
        Positive = White advantage, Negative = Black advantage.
        """
        # Checkmate/Stalemate
        if board.is_checkmate():
            if board.active_color == WHITE:
                return -(self.CHECKMATE + depth)
            else:
                return self.CHECKMATE + depth
        if board.is_draw():
            return 0

        score = 0

        for piece, square in board.get_pieces():
            material_value = PIECE_VALUE_TABLE[piece]
            positional_value = BOARD_VALUE_TABLE[piece][square]
            if piece & WHITE:
                score += (material_value + positional_value)
            else:
                score -= (material_value + positional_value)

        return score
