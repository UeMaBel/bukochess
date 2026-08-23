from pydantic import BaseModel


class LLMDecision(BaseModel):
    move: str
    explanation: str
