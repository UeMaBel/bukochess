import { afterEach, describe, expect, it, vi } from "vitest";

import { gameStatus, makeMove, makeMoveFast } from "../game";


const WHITE_FEN = "8/8/8/8/8/8/4P3/4K2k w - - 0 1";
const BLACK_FEN = "8/8/4p3/8/8/8/8/4K2k b - - 0 1";


function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}


function mockFetch(response: Response): ReturnType<typeof vi.fn<typeof fetch>> {
  const fetchMock = vi.fn<typeof fetch>().mockResolvedValue(response);
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}


afterEach(() => {
  vi.unstubAllGlobals();
});


describe("makeMoveFast", () => {
  it.each([
    ["w", WHITE_FEN, "e2e4"],
    ["b", BLACK_FEN, "e6e5"],
  ] as const)("posts and returns a %s move", async (color, fen, move) => {
    const responseBody = {
      fen: `${fen}-updated`,
      played_color: color,
      engine: "Human" as const,
      move,
    };
    const fetchMock = mockFetch(jsonResponse(responseBody));

    await expect(makeMoveFast(fen, move)).resolves.toEqual(responseBody);
    expect(fetchMock).toHaveBeenCalledWith("/api/v1/game/fast-move", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ fen, move }),
    });
  });

  it("throws the FastAPI detail message", async () => {
    mockFetch(jsonResponse({ detail: "invalid move format" }, 400));

    await expect(makeMoveFast(WHITE_FEN, "e9e4")).rejects.toThrow(
      "invalid move format",
    );
  });

  it("uses its fallback error message", async () => {
    mockFetch(jsonResponse({}, 500));

    await expect(makeMoveFast(WHITE_FEN, "e2e4")).rejects.toThrow(
      "Fast move failed",
    );
  });

  it("propagates network errors", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn<typeof fetch>().mockRejectedValue(new Error("Network unavailable")),
    );

    await expect(makeMoveFast(WHITE_FEN, "e2e4")).rejects.toThrow(
      "Network unavailable",
    );
  });
});


describe("makeMove", () => {
  it("posts a move and returns the validated move response", async () => {
    const responseBody = {
      fen: `${WHITE_FEN}-updated`,
      status: "ok",
      legal_moves: ["h1g1"],
    };
    const fetchMock = mockFetch(jsonResponse(responseBody));

    await expect(makeMove(WHITE_FEN, "e2e4")).resolves.toEqual(responseBody);
    expect(fetchMock).toHaveBeenCalledWith("/api/v1/game/move", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ fen: WHITE_FEN, move: "e2e4" }),
    });
  });

  it("throws the FastAPI detail message", async () => {
    mockFetch(jsonResponse({ detail: "illegal move" }, 400));

    await expect(makeMove(WHITE_FEN, "e2e5")).rejects.toThrow("illegal move");
  });

  it("uses its fallback error message", async () => {
    mockFetch(jsonResponse({}, 500));

    await expect(makeMove(WHITE_FEN, "e2e4")).rejects.toThrow("Move failed");
  });

  it("propagates network errors", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn<typeof fetch>().mockRejectedValue(new Error("Network unavailable")),
    );

    await expect(makeMove(WHITE_FEN, "e2e4")).rejects.toThrow(
      "Network unavailable",
    );
  });
});


describe("gameStatus", () => {
  it.each([
    ["w", WHITE_FEN],
    ["b", BLACK_FEN],
  ] as const)("posts and returns the %s game status", async (color, fen) => {
    const responseBody = {
      fen,
      active_color: color,
      in_check: false,
      status: "ok",
    };
    const fetchMock = mockFetch(jsonResponse(responseBody));

    await expect(gameStatus({ fen })).resolves.toEqual(responseBody);
    expect(fetchMock).toHaveBeenCalledWith("/api/v1/game/status", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ fen }),
    });
  });

  it("throws the FastAPI detail message", async () => {
    mockFetch(jsonResponse({ detail: "Invalid board layout" }, 400));

    await expect(gameStatus({ fen: "invalid" })).rejects.toThrow(
      "Invalid board layout",
    );
  });

  it("uses its fallback error message", async () => {
    mockFetch(jsonResponse({}, 500));

    await expect(gameStatus({ fen: WHITE_FEN })).rejects.toThrow(
      "Game status failed",
    );
  });

  it("propagates network errors", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn<typeof fetch>().mockRejectedValue(new Error("Network unavailable")),
    );

    await expect(gameStatus({ fen: WHITE_FEN })).rejects.toThrow(
      "Network unavailable",
    );
  });
});
