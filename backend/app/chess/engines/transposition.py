from dataclasses import dataclass
from typing import Optional

TT_EXACT = 0
TT_LOWER = 1  # fail-high
TT_UPPER = 2  # fail-low


@dataclass
class TTEntry:
    depth: int
    score: int
    flag: int
    best_move: Optional[tuple[int, int, int]]


class TranspositionTable:
    def __init__(self):
        self.table: dict[int, TTEntry] = {}

    def probe(self, key: int, depth: int, alpha: int, beta: int):
        entry = self.table.get(key)
        if entry is None or entry.depth < depth:
            return None

        if entry.flag == TT_EXACT:
            return entry.score
        elif entry.flag == TT_LOWER and entry.score >= beta:
            return entry.score
        elif entry.flag == TT_UPPER and entry.score <= alpha:
            return entry.score

        return None

    def store(self, key: int, depth: int, score: int, flag: int, best_move):
        old = self.table.get(key)
        if old is None or depth >= old.depth:
            self.table[key] = TTEntry(depth, score, flag, best_move)
