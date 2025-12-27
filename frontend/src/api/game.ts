export interface MoveResponse {
  fen: string;
  status: string;
  legal_moves: number;
}

export async function makeMove(fen: string, move: string): Promise<MoveResponse> {
  const res = await fetch("/api/v1/game/move", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ fen, move }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
