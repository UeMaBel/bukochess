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
  square?: string;
}
export interface LegalMovesResponse {
  moves: string[];
}

export async function getLegalMoves(
  request: LegalMovesRequest,
): Promise<LegalMovesResponse> {
  const res = await fetch("/api/v1/position/legal-moves", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      fen: request.fen,
      square: request.square ?? "",
    }),
  });

  if (!res.ok) {
    const error: { detail?: string } = await res.json();
    throw new Error(error.detail ?? "Legal moves request failed");
  }

  return res.json();
}
