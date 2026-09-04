import time

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    LengthFinishReasonError,
    OpenAI,
    RateLimitError,
)
from pydantic import BaseModel

from app.ai.models import (
    LLMDecision,
    LLMDecisionMetadata,
    LLMProviderMetadata,
    LLMProviderResult,
)
from app.ai.settings import LLMSettings
from app.core.config import settings
from app.core.exceptions import (
    LLMMaxOutputTokensException,
    LLMProviderException,
)


class OpenAIMove(BaseModel):
    move: str


class OpenAIMoveWithExplanation(BaseModel):
    move: str
    explanation: str


class OpenAIProvider:
    def __init__(self, llm_settings: LLMSettings):
        self.settings = llm_settings

        # Automatically reads OPENAI_API_KEY from the environment.
        self.client = OpenAI(
            api_key=settings.openai_api_key.get_secret_value(),
            timeout=120.0,
            max_retries=2,
        )

    def choose_move(
        self,
        fen: str,
        legal_moves: list[str],
    ) -> LLMProviderResult:
        if not legal_moves:
            raise LLMProviderException(
                "no_legal_moves",
                "No legal moves provided to OpenAI.",
                retryable=False,
            )

        started = time.perf_counter()

        try:
            response = self.client.responses.parse(
                model=self.settings.model,
                instructions=(
                    "You are a chess engine. "
                    "Choose the strongest legal move in the given position. "
                    "The returned move must be exactly one of the supplied legal moves "
                    "and must use UCI notation."
                ),
                input=(f"FEN: {fen}\nLegal moves: {', '.join(legal_moves)}"),
                text_format=(
                    OpenAIMoveWithExplanation
                    if self.settings.explanation
                    else OpenAIMove
                ),
                max_output_tokens=self.settings.max_output_tokens,
                reasoning={
                    "effort": self.settings.reasoning_effort,
                },
                # temperature=self.settings.temperature,
            )

        except APITimeoutError as exc:
            raise LLMProviderException(
                "timeout",
                "The OpenAI request timed out.",
                retryable=True,
            ) from exc

        except RateLimitError as exc:
            raise LLMProviderException(
                "rate_limit",
                "OpenAI rate limit reached.",
                retryable=True,
            ) from exc

        except LengthFinishReasonError as exc:
            raise LLMMaxOutputTokensException("OpenAI") from exc

        except APIConnectionError as exc:
            raise LLMProviderException(
                "connection_error",
                "Could not connect to OpenAI.",
                retryable=True,
            ) from exc

        except APIStatusError as exc:
            raise LLMProviderException(
                "provider_error",
                f"OpenAI API error ({exc.status_code}).",
                retryable=exc.status_code >= 500,
            ) from exc

        except Exception as exc:
            raise LLMProviderException(
                "unexpected_error",
                "OpenAI could not choose a move.",
                retryable=False,
            ) from exc

        latency_ms = round((time.perf_counter() - started) * 1000)

        parsed = response.output_parsed

        if parsed is None:
            incomplete_details = getattr(response, "incomplete_details", None)
            if (
                getattr(response, "status", None) == "incomplete"
                and getattr(incomplete_details, "reason", None) == "max_output_tokens"
            ):
                raise LLMMaxOutputTokensException("OpenAI")

            raise LLMProviderException(
                "invalid_response",
                "OpenAI returned no structured chess decision.",
                retryable=True,
            )

        explanation = (
            parsed.explanation
            if isinstance(parsed, OpenAIMoveWithExplanation)
            else None
        )
        decision = LLMDecision(
            move=parsed.move,
            metadata=LLMDecisionMetadata(
                explanation=explanation,
            ),
        )
        usage = response.usage
        result = LLMProviderResult(
            decision=decision,
            metadata=LLMProviderMetadata(
                input_tokens=usage.input_tokens if usage else None,
                output_tokens=usage.output_tokens if usage else None,
                latency_ms=latency_ms,
            ),
        )
        return result
