from abc import ABC, abstractmethod

from app.ai.models import LLMProviderResult
from app.ai.settings import LLMSettings


class LLMProvider(ABC):
    def __init__(self, settings: LLMSettings):
        self.settings = settings

    @abstractmethod
    def choose_move(self, fen: str, legal_moves: list[str]) -> LLMProviderResult:
        pass
