export interface EngineMoveResponse {
  fen: string;
  move: string;
  status: string;
}

export async function getEngineMove(fen: string, engine: string): Promise<EngineMoveResponse> {
  const res = await fetch("/api/v1/engine/move", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ fen, engine }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
