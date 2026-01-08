from app.chess.perft import run_perft
from app.chess.move_mailbox import MoveMailBoxGenerator as MoveGenerator, BoardMailbox as Board
from app.chess.engines.alphabeta import AlphaBeta
from app.chess.utils import to_uci
import time


def eval(depth: int):
    board = Board()
    board.from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq f6 0 3")
    gen = MoveGenerator(board)
    # Start position
    history = []
    engine = AlphaBeta(depth)
    print(f"Start Pos Eval: {engine.evaluate_position(board, depth)}")

    # Test 2: After 1. e4
    board.from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq f6 0 3")
    gen = MoveGenerator(board)
    gen.apply_uci("e2e4")
    print(f"After e4 Eval: {engine.evaluate_position(board, depth)}")

    # Test 3: After 1. h3
    board.from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq f6 0 3")
    gen = MoveGenerator(board)
    gen.apply_uci("e2e3")
    print(f"After e2e3 Eval: {engine.evaluate_position(board, depth)}")


def self_play_test(depth, moves_to_play=10):
    board = Board()
    board.from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq f6 0 3")
    gen = MoveGenerator(board)
    # Start position
    history = []
    engine = AlphaBeta(depth)

    print(f"Starting Self-Play Test (Depth {depth})")
    print("-" * 30)

    for i in range(moves_to_play):
        # 1. Engine thinks
        move = engine.choose_move(gen.board)

        # 2. Log the "Perspective"
        # If it's Black's turn, the score should be negative if White is winning

        if move is None:
            print("Game Over (Checkmate or Stalemate)")
            break

        gen.apply_uci(move)
        history.append(move)
        gen.board.print_board()

    return history


def run_profile(depth: int):
    print(f"Starting pofile depth {depth}...")

    start_time = time.perf_counter()
    # self_play_test(depth, 1)
    eval(depth)
    end_time = time.perf_counter()

    duration = end_time - start_time
    # Avoid division by zero if duration is 0
    # nps = int(total_nodes / duration) if duration > 0 else 0

    print(f"--- Results ---")
    print(f"Depth:      {depth}")
    # print(f"Nodes:      {total_nodes}")
    print(f"Time:       {duration:.3f} s")
    # print(f"NPS:        {nps:,}")  # Format with commas for readability
    # return total_nodes


def profile(depth):
    fen = "r3k2r/8/8/8/8/8/8/4K3 w kq - 0 1"
    fen_2 = "8/8/8/8/8/8/6k1/4K2R w K - 0 1"
    fen_3 = "8/8/8/8/8/8/1k6/R3K3 w Q - 0 1"
    fen_4 = "rnbqkb1r/ppppp1pp/7n/4Pp2/8/8/PPPP1PPP/RNBQKBNR w KQkq f6 0 3"
    b = Board()
    b.from_fen(fen_4)
    gen = MoveGenerator(b)
    en = AlphaBeta(depth)
    # run_perft(gen, deepness)
    print(en.choose_move(b))
    print(f"nodes: {en.nodes}, cutoffs: {en.cutoffs}, fm_cuttoffs: {en.first_move_cutoffs}, tt: {en.tt_hits}")


run_profile(5)
