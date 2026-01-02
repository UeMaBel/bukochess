from app.chess.engines.dumb_engine import DumbEngine
from app.chess.engines.alphabeta import AlphaBeta
from app.chess.engines.random_engine import RandomEngine, BoardArray
from app.chess.move_tuple import MoveTupleGenerator
from app.core.utils import measure_time

board = BoardArray()
board.from_fen("rnbqkbnr/ppp1pppp/8/3p4/2P5/8/PP1PPPPP/RNBQKBNR w KQkq d6 0 1")
engine = RandomEngine()
engine_dumb = DumbEngine()
engine_alphabeta = AlphaBeta()
gen = MoveTupleGenerator(board, order=True)


@measure_time
def in_loop(idx):
    print(f"{board.active_color}s turn")
    if board.is_checkmate(board.active_color):
        print("Game over - checkmate")
    if board.is_stalemate(board.active_color):
        print("Game over - stalemate")
    if board.is_insufficient_material():
        print("Game over - insufficient material")
    m = engine_alphabeta.choose_move(gen)
    if m is None:
        print("Game over")
        return

    print(f"{str(idx)}: {board.active_color} is moving {str(m)} calc nodes: {engine_alphabeta.nodes}")
    gen.apply(m)
    print(f"fen: {board.to_fen()}")
    print(board.print_board())


@measure_time
def loop():
    idx = 1
    while idx != 5:
        in_loop(idx)
        idx += 1


board.print_board()
loop()
