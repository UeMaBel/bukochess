import time

from openai import OpenAI, APIConnectionError, APIStatusError, RateLimitError
from pydantic import BaseModel

from app.core.config import settings
from app.ai.models import (
    LLMDecision,
    LLMDecisionMetadata,
    LLMProviderMetadata,
    LLMProviderResult,
)
from app.ai.settings import LLMSettings
from app.core.exceptions import BukochessException


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

    def choose_move(self, fen: str, legal_moves: list[str], ) -> LLMProviderResult:
        if not legal_moves:
            raise BukochessException("No legal moves provided to OpenAI")

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
                input=(
                    f"FEN: {fen}\n"
                    f"Legal moves: {', '.join(legal_moves)}"
                ),
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

        except RateLimitError as exc:
            raise BukochessException(
                "OpenAI rate limit reached"
            ) from exc

        except APIConnectionError as exc:
            raise BukochessException(
                "Could not connect to OpenAI"
            ) from exc

        except APIStatusError as exc:
            raise BukochessException(
                f"OpenAI API error ({exc.status_code})"
            ) from exc

        latency_ms = round(
            (time.perf_counter() - started) * 1000
        )

        parsed = response.output_parsed

        if parsed is None:
            raise BukochessException(
                "OpenAI returned no structured chess decision"
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
