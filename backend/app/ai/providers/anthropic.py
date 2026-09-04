from app.ai.models import LLMProviderResult
from app.ai.provider import LLMProvider
from app.ai.settings import LLMSettings


class AnthropicProvider(LLMProvider):
    def __init__(self, settings: LLMSettings):
        super().__init__(settings)

    def choose_move(self, fen: str, legal_moves: list[str], ) -> LLMProviderResult:
        raise NotImplementedError
