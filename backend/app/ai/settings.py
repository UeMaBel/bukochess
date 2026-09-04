from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class LLMSettings(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    provider: Literal["openai", "anthropic", "local"]
    model: str

    reasoning_effort: Literal["none", "low", "medium", "high"] = Field(
        default="none",
        alias="reasoningEffort",
    )

    temperature: float = Field(
        default=0.0,
        ge=0.0,
        le=2.0,
    )

    max_output_tokens: int = Field(
        default=64,
        ge=1,
        alias="maxOutputTokens",
    )

    explanation: bool = False

    def __str__(self):
        return (f"provider: {self.provider}, model {self.model}, "
                f"reasoning: {self.reasoning_effort}, temp: {self.temperature}, max_output: {self.max_output_tokens}, explanation: {self.explanation}")
