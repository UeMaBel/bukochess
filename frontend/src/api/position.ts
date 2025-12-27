export interface BoardResponse {
  board: string[][];
  fen: string;
}

export async function importFEN(fen: string): Promise<BoardResponse> {
  const res = await fetch("/api/v1/position/fen", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ fen }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
