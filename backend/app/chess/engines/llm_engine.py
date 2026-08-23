from app.chess.engines.base import Engine
from app.chess.move_mailbox import MoveMailBoxGenerator as MoveGenerator, BoardMailbox as Board
from app.ai.settings import LLMSettings
from app.ai.providers.openai import OpenAIProvider
from app.ai.providers.anthropic import AnthropicProvider
from app.ai.providers.local import LocalProvider


class LLMEngine(Engine):
    def __init__(self, settings: LLMSettings):
        super().__init__()
        self.settings = settings
        self.provider = self._create_provider()

    def choose_move(self, board: Board):
        print(f"searching move with llm. Settings: {self.settings}")

    def _create_provider(self):
        match self.settings.provider:
            case "openai":
                return OpenAIProvider(self.settings)
            case "anthropic":
                return AnthropicProvider(self.settings)
            case "local":
                return LocalProvider(self.settings)
            case _:
                raise ValueError(
                    f"Unsupported LLM provider: {self.settings.provider}"
                )
