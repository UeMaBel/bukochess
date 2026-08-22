export type EngineId = "random" | "dumb" | "alphabeta";

export interface RandomEngineSettings {
  seed?: number;
}

export interface DumbEngineSettings {
  depth: number;
  seed?: number;
}

export interface AlphaBetaEngineSettings {
  depth: number;
  seed?: number;
}

export interface EngineRequestMetadataByEngine {
  random: RandomEngineSettings;
  dumb: DumbEngineSettings;
  alphabeta: AlphaBetaEngineSettings;
}

export interface BaseEngineResponseMetadata {
  name: string;
}

export interface RandomEngineResponseMetadata extends BaseEngineResponseMetadata {
  seed?: number;
}

export interface DumbEngineResponseMetadata extends BaseEngineResponseMetadata {
  depth: number;
  evaluation: number;
  seed?: number;
}

export interface AlphaBetaEngineResponseMetadata extends BaseEngineResponseMetadata {
  depth: number;
  evaluation: number;
  nodes: number;
  cutoffs: number;
  tt_hits: number;
  quiesce_calls: number;
  seed?: number;
}

export interface EngineResponseMetadataByEngine {
  random: RandomEngineResponseMetadata;
  dumb: DumbEngineResponseMetadata;
  alphabeta: AlphaBetaEngineResponseMetadata;
}

export type EngineMoveRequest = {
  [E in EngineId]: {
    fen: string;
    engine: E;
    metadata: EngineRequestMetadataByEngine[E];
  };
}[EngineId];

export type EngineMoveResponse = {
  [E in EngineId]: {
    fen: string;
    move: string;
    status: string;
    engine: E;
    played_color: "w" | "b";
    metadata: EngineResponseMetadataByEngine[E];
  };
}[EngineId];

export async function getEngineMove(
  req: EngineMoveRequest
): Promise<EngineMoveResponse> {
  const res = await fetch("/api/v1/engine/move", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail ?? "engine error");
  }

  return res.json();
}
