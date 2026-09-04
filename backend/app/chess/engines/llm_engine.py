from app.ai.models import LLMError
from app.ai.providers.anthropic import AnthropicProvider
from app.ai.providers.local import LocalProvider
from app.ai.providers.openai import OpenAIProvider
from app.ai.settings import LLMSettings
from app.chess.engines.base import Engine
from app.chess.engines.models import EngineResult
from app.chess.move_mailbox import BoardMailbox as Board
from app.chess.move_mailbox import MoveMailBoxGenerator as MoveGenerator
from app.chess.static import WHITE
from app.chess.utils import to_uci
from app.core.config import settings as app_settings
from app.core.exceptions import LLMProviderException


class LLMEngine(Engine):
    def __init__(self, settings: LLMSettings):
        super().__init__()
        self.settings = settings
        self.configuration_error = self._configuration_error()
        self.provider = (
            None if self.configuration_error is not None else self._create_provider()
        )
        self.engine_name = "LLM"

    def choose_move(self, board: Board) -> EngineResult:
        gen = MoveGenerator(board)
        fen = board.to_fen()

        legal_moves = [to_uci(move) for move in gen.legal_moves()]

        if not legal_moves:
            return None

        if self.configuration_error is not None:
            return self._error_result(board, self.configuration_error)

        try:
            assert self.provider is not None
            provider_result = self.provider.choose_move(fen, legal_moves)
        except LLMProviderException as exc:
            return self._error_result(board, exc)
        except Exception:
            return self._error_result(
                board,
                LLMProviderException(
                    "unexpected_error",
                    f"The {self.settings.provider} provider could not choose a move.",
                    retryable=False,
                ),
            )
        decision = provider_result.decision

        if decision.move not in legal_moves:
            return self._error_result(
                board,
                LLMProviderException(
                    "illegal_move",
                    "The LLM returned a move that is not legal in this position.",
                    retryable=True,
                ),
            )
        result = EngineResult(
            engine_name=self.engine_name,
            move=decision.move,
            played_color="w" if board.active_color == WHITE else "b",
            metadata={
                **self.settings.model_dump(),
                **decision.metadata.model_dump(),
                **provider_result.metadata.model_dump(),
            },
        )
        return result

    def _error_result(self, board: Board, error: LLMProviderException) -> EngineResult:
        return EngineResult(
            engine_name=self.engine_name,
            move=None,
            played_color="w" if board.active_color == WHITE else "b",
            metadata={
                **self.settings.model_dump(),
                "error": LLMError(
                    code=error.code,
                    message=error.message,
                    retryable=error.retryable,
                ).model_dump(),
            },
        )

    def _create_provider(self):
        match self.settings.provider:
            case "openai":
                return OpenAIProvider(self.settings)
            case "anthropic":
                return AnthropicProvider(self.settings)
            case "local":
                return LocalProvider(self.settings)
            case _:
                raise ValueError(f"Unsupported LLM provider: {self.settings.provider}")

    def _configuration_error(self) -> LLMProviderException | None:
        if (
            self.settings.provider == "openai"
            and not app_settings.openai_api_key.get_secret_value().strip()
        ):
            return LLMProviderException(
                "missing_api_key",
                "OpenAI is not configured. Add OPENAI_API_KEY to the environment.",
                retryable=False,
            )
        return None
