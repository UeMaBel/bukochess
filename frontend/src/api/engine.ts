import type { AIPlayerSettings } from "./aiSettings";


export type EngineId = "random" | "dumb" | "alphabeta" | "llm";
export type EngineResponseName =
  | "Random Engine"
  | "Dumb Engine"
  | "Alpha Beta Engine"
  | "LLM";

export interface RandomEngineSettings {
  seed?: number;
}

export interface DumbEngineSettings {
  depth: number;
  seed?: number;
}

export interface AlphaBetaEngineSettings {
  depth?: number;
  seed?: number;
}

export type LLMEngineSettings = AIPlayerSettings;

export interface EngineRequestMetadataByEngine {
  random: RandomEngineSettings;
  dumb: DumbEngineSettings;
  alphabeta: AlphaBetaEngineSettings;
  llm: LLMEngineSettings;
}

export type EngineMoveRequest = {
  [Engine in EngineId]: {
    fen: string;
    engine: Engine;
    metadata: EngineRequestMetadataByEngine[Engine];
  };
}[EngineId];

interface BaseEngineMoveResponse {
  fen: string;
  status: string;
  played_color: "w" | "b";
}

export interface RandomEngineResponse extends BaseEngineMoveResponse {
  engine: "Random Engine";
  move: string;
  metadata: {
    seed: number | null;
  };
}

export interface DumbEngineResponse extends BaseEngineMoveResponse {
  engine: "Dumb Engine";
  move: string;
  metadata: {
    depth: number;
    seed: number | null;
  };
}

export interface AlphaBetaEngineResponse extends BaseEngineMoveResponse {
  engine: "Alpha Beta Engine";
  move: string;
  metadata: {
    depth: number;
    seed: number | null;
  };
}

export interface EngineError {
  code: string;
  message: string;
  retryable: boolean;
}

interface BaseLLMMetadata {
  provider: string;
  model: string;
  reasoning_effort: "none" | "low" | "medium" | "high";
  temperature: number;
  max_output_tokens: number;
}

export interface LLMSuccessResponse extends BaseEngineMoveResponse {
  engine: "LLM";
  move: string;
  metadata: BaseLLMMetadata & {
    explanation: string | null;
    confidence: number | null;
    input_tokens: number | null;
    output_tokens: number | null;
    latency_ms: number | null;
  };
}

export interface LLMErrorResponse extends BaseEngineMoveResponse {
  engine: "LLM";
  move: null;
  metadata: BaseLLMMetadata & {
    explanation: boolean;
    error: EngineError;
  };
}

export type EngineMoveResponse =
  | RandomEngineResponse
  | DumbEngineResponse
  | AlphaBetaEngineResponse
  | LLMSuccessResponse
  | LLMErrorResponse;

async function throwApiError(response: Response): Promise<never> {
  const error: { detail?: string } = await response.json();
  throw new Error(error.detail ?? "Engine move failed");
}

export async function getEngineMove(
  request: EngineMoveRequest,
): Promise<EngineMoveResponse> {
  const response = await fetch("/api/v1/engine/move", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    return throwApiError(response);
  }

  return response.json();
}
