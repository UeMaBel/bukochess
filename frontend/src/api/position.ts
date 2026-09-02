export interface FENRequest {
  fen: string;
}

export interface BoardResponse {
  board: string[][];
  fen: string;
}

export async function importFEN(fen: string): Promise<BoardResponse> {
  const request: FENRequest = { fen };
  const res = await fetch("/api/v1/position/fen", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!res.ok) {
    const error: { detail?: string } = await res.json();
    throw new Error(error.detail ?? "FEN import failed");
  }

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
