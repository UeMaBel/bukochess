import requests

API_URL = "http://127.0.0.1:8000/api/v1"


def print_board(fen: str):
    print()
    print("    A   B   C   D   E   F   G   H")
    print("  +---+---+---+---+---+---+---+---+")

    row_idx = 0
    for row in fen.split()[0].split("/"):
        rank = 8 - row_idx
        row_str = f"{rank} |"
        for square in row:
            if square.isdigit():
                row_str += " . |" * int(square)
            else:
                piece = square if square != "" else "."
                row_str += f" {piece} |"
        print(row_str)
        print("  +---+---+---+---+---+---+---+---+")
        row_idx += 1

    print("    A   B   C   D   E   F   G   H")
    print()


def get_legal_moves(fen: str, square: str):
    resp = requests.post(f"{API_URL}/position/legal-moves", json={"fen": fen, "square": square})
    if resp.status_code != 200:
        return []
    return resp.json()["moves"]


def make_move(fen: str, move: str):
    resp = requests.post(f"{API_URL}/game/move", json={"fen": fen, "move": move})
    if resp.status_code != 200:
        print("Illegal move or server error.")
        return None
    return resp.json()


def engine_move(fen: str, engine: str = "random", seed: int | None = None):
    payload = {"fen": fen, "engine": engine}
    if seed is not None:
        payload["seed"] = seed
    resp = requests.post(f"{API_URL}/engine/move", json=payload)

    if resp.status_code != 200:
        print("Engine move failed")
        return None
    return resp.json()


def main():
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    resp = requests.post(f"{API_URL}/health")
    print(resp)
    engine = input("Which engine? (r=random, h=other human): ")
    engine.lower()
    if not (engine == "r" or engine == "h"):
        print(f"{engine} not valid.")
        exit()

    color = "w"
    if engine != "h":
        color = input("Black or white (b/w): ")
        color = color.lower()
        if not (color == "b" or color == "w"):
            print(f"{color} is not a color.")
            exit()
    if engine == "r": engine = "random"

    if color == "b":  # engine makes first move
        print_board(fen)  # Engine plays
        engine_result = engine_move(fen, engine)
        if engine_result is None:
            print("Engine failed, exiting")
            exit()
        fen = engine_result["fen"]
        print(f"Engine plays: {engine_result['move']}")
        if engine_result["status"] in ("checkmate", "draw"):
            print(f"Game over: {engine_result['status']}")
            exit()

    while True:
        print_board(fen)
        move_input = input("Your move (e2e4): ").strip()
        result = make_move(fen, move_input)
        if result is None:
            continue

        fen = result["fen"]
        print(f"Move applied. Status: {result['status']}")

        if result["status"] in ("checkmate", "draw"):
            print(f"Game over: {result['status']}")
            break

        # Engine plays
        engine_result = engine_move(fen, engine)
        if engine_result is None:
            print("Engine failed, exiting")
            break
        fen = engine_result["fen"]
        print(f"Engine plays: {engine_result['move']}")
        if engine_result["status"] in ("checkmate", "draw"):
            print(f"Game over: {engine_result['status']}")
            break


if __name__ == "__main__":
    main()
