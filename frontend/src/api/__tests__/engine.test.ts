import { afterEach, describe, expect, it, vi } from "vitest";

import type { EngineMoveRequest, EngineMoveResponse } from "../engine";
import { getEngineMove } from "../engine";


const FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";


function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}


afterEach(() => {
  vi.unstubAllGlobals();
});


describe("getEngineMove", () => {
  it.each<EngineMoveRequest>([
    { fen: FEN, engine: "random", metadata: { seed: 7 } },
    { fen: FEN, engine: "dumb", metadata: { depth: 1, seed: 7 } },
    { fen: FEN, engine: "alphabeta", metadata: { depth: 2, seed: 7 } },
    {
      fen: FEN,
      engine: "llm",
      metadata: {
        provider: "openai",
        model: "test-model",
        reasoningEffort: "medium",
        temperature: 0.2,
        maxOutputTokens: 128,
        explanation: false,
      },
    },
  ])("posts the $engine request without changing its metadata", async (request) => {
    const responseBody: EngineMoveResponse = {
      fen: `${FEN}-updated`,
      move: "e2e4",
      status: "ok",
      engine: "Random Engine",
      played_color: "w",
      metadata: { seed: 7 },
    };
    const fetchMock = vi.fn<typeof fetch>().mockResolvedValue(
      jsonResponse(responseBody),
    );
    vi.stubGlobal("fetch", fetchMock);

    await expect(getEngineMove(request)).resolves.toEqual(responseBody);
    expect(fetchMock).toHaveBeenCalledWith("/api/v1/engine/move", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    });
  });

  it("returns an LLM error response with an unchanged position", async () => {
    const request: EngineMoveRequest = {
      fen: FEN,
      engine: "llm",
      metadata: {
        provider: "openai",
        model: "test-model",
        reasoningEffort: "medium",
        temperature: 0.2,
        maxOutputTokens: 128,
        explanation: false,
      },
    };
    const responseBody: EngineMoveResponse = {
      fen: FEN,
      move: null,
      status: "ok",
      engine: "LLM",
      played_color: "w",
      metadata: {
        provider: "openai",
        model: "test-model",
        reasoning_effort: "medium",
        temperature: 0.2,
        max_output_tokens: 128,
        explanation: false,
        error: {
          code: "timeout",
          message: "The OpenAI request timed out.",
          retryable: true,
        },
      },
    };
    vi.stubGlobal(
      "fetch",
      vi.fn<typeof fetch>().mockResolvedValue(jsonResponse(responseBody)),
    );

    await expect(getEngineMove(request)).resolves.toEqual(responseBody);
  });

  it("throws the FastAPI detail message", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn<typeof fetch>().mockResolvedValue(
        jsonResponse({ detail: "Unknown engine: invalid" }, 400),
      ),
    );

    await expect(
      getEngineMove({ fen: FEN, engine: "random", metadata: {} }),
    ).rejects.toThrow("Unknown engine: invalid");
  });

  it("uses a fallback when an error response has no detail", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn<typeof fetch>().mockResolvedValue(jsonResponse({}, 500)),
    );

    await expect(
      getEngineMove({ fen: FEN, engine: "random", metadata: {} }),
    ).rejects.toThrow("Engine move failed");
  });

  it("propagates network errors", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn<typeof fetch>().mockRejectedValue(new Error("Network unavailable")),
    );

    await expect(
      getEngineMove({ fen: FEN, engine: "random", metadata: {} }),
    ).rejects.toThrow("Network unavailable");
  });
});
