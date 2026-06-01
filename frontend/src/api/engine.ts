export interface EngineMoveRequest {
  fen: string;
  engine: string;
  seed?: number;
  depth: number;
}

export interface EngineMoveResponse {
  fen: string;
  move: string;
  status: string;
  evaluation: number;
  depth: number;
  nodes: number;
  nps: number;
  pv: string[];
  engine: string;
  played_color: string;
}

export async function getEngineMove(
  req: EngineMoveRequest
): Promise<EngineMoveResponse> {
  const res = await fetch("/api/v1/engine/move", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
    console.log(req.engine)

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail ?? "engine error");
  }

  return res.json();
}
