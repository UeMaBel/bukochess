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

export interface LegalMovesRequest {
  fen: string;
  square: string;
}
export interface LegalMovesResponse {
  legal_moves: string[];
}

export async function getLegalMoves(req: LegalMovesRequest
): Promise<LegalMovesResponse> {
    req.square="";
  const res = await fetch("/api/v1/position/legal-moves", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify( req ),
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail ?? "status error");
  }

  return res.json();
}