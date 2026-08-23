from abc import ABC, abstractmethod
from app.ai.settings import LLMSettings
from app.ai.models import LLMDecision


class LLMProvider(ABC):
    def __init__(self, settings: LLMSettings):
        self.settings = settings

    @abstractmethod
    def choose_move(self, fen: str, legal_moves: list[str]) -> LLMDecision:
        raise NotImplementedError
