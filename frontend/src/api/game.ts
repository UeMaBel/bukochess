export interface MoveResponse {
  fen: string;
  status: string;
  legal_moves: number;
}

export async function makeMove(fen: string, move: string): Promise<MoveResponse> {
  const res = await fetch("/api/v1/game/move", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({fen, move}),
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail);
  }

  return res.json();
}

export interface GameStatusRequest {
  fen: string;
}

export interface GameStatusResponse {
  fen: string;
  active_color: string;
  in_check: boolean;
  status: string;
}

export async function gameStatus(
  req: GameStatusRequest
): Promise<GameStatusResponse> {
  const res = await fetch("/api/v1/game/status", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail ?? "status error");
  }

  return res.json();
}

