from pydantic import BaseModel


class LLMDecisionMetadata(BaseModel):
    explanation: str | None = None
    confidence: float | None = None


class LLMDecision(BaseModel):
    move: str
    metadata: LLMDecisionMetadata


class LLMProviderMetadata(BaseModel):
    input_tokens: int | None = None
    output_tokens: int | None = None
    latency_ms: int | None = None


class LLMProviderResult(BaseModel):
    decision: LLMDecision
    metadata: LLMProviderMetadata
