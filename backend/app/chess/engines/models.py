from typing import Any
from pydantic import BaseModel, Field


class EngineResult(BaseModel):
    engine_name: str
    move: str
    played_color: str
    metadata: dict[str, Any] = Field(default_factory=dict)
