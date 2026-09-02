export interface MoveRequest {
  fen: string;
  move: string;
}

export interface MoveResponseFast {
  fen: string;
  played_color: "w" | "b";
  engine: "Human";
  move: string;
}

export interface MoveResponse {
  fen: string;
  status: string;
  legal_moves: string[];
}

export interface GameStatusRequest {
  fen: string;
}

export interface GameStatusResponse {
  fen: string;
  active_color: "w" | "b";
  in_check: boolean;
  status: string;
}

async function throwApiError(response: Response, fallback: string): Promise<never> {
  const error: { detail?: string } = await response.json();
  throw new Error(error.detail ?? fallback);
}

export async function makeMoveFast(
  fen: string,
  move: string,
): Promise<MoveResponseFast> {
  const request: MoveRequest = { fen, move };
  const response = await fetch("/api/v1/game/fast-move", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    return throwApiError(response, "Fast move failed");
  }

  return response.json();
}

export async function makeMove(
  fen: string,
  move: string,
): Promise<MoveResponse> {
  const request: MoveRequest = { fen, move };
  const response = await fetch("/api/v1/game/move", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    return throwApiError(response, "Move failed");
  }

  return response.json();
}

export async function gameStatus(
  request: GameStatusRequest,
): Promise<GameStatusResponse> {
  const response = await fetch("/api/v1/game/status", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    return throwApiError(response, "Game status failed");
  }

  return response.json();
}
