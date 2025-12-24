from app.chess.board_array import BoardArray
from app.chess.engines.random_engine import RandomEngine

board = BoardArray()
board.from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
engine = RandomEngine()

while True:
    if board.is_checkmate(board.active_color):
        print("Game over - checkmate")
    if board.is_stalemate(board.active_color):
        print("Game over - stalemate")
    if board.is_insufficient_material():
        print("Game over - insufficient material")
    move = engine.choose_move(board)
    if move is None:
        print("Game over")
        break

    undo = move.apply(board)
    print(board.print_board())
