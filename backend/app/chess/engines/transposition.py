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
    move: tuple[int, int, int]


class TranspositionTable:
    def __init__(self):
        self.table: dict[int, TTEntry] = {}

    def get_entry(self, key: int):
        """Returns the full entry object if it exists, otherwise None."""
        return self.table.get(key)

    def store(self, key: int, depth: int, score: int, flag: int, move: tuple[int, int, int]):
        # Always replace if the new search was deeper
        existing = self.table.get(key)
        if existing is None or depth >= existing.depth:
            self.table[key] = TTEntry(score, depth, flag, move)
