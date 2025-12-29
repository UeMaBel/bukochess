export interface EngineMoveRequest {
  fen: string;
  engine: string;
  seed?: number;
}

export interface EngineMoveResponse {
  fen: string;
  move: string;
  status: string;
}

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
