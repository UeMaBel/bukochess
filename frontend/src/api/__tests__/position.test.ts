import { afterEach, describe, expect, it, vi } from "vitest";

import { importFEN } from "../position";


const FEN = "8/8/8/8/8/8/8/4K2k w - - 0 1";


function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}


afterEach(() => {
  vi.unstubAllGlobals();
});


describe("importFEN", () => {
  it("posts the FEN and returns the parsed board response", async () => {
    const responseBody = {
      fen: FEN,
      board: [
        [".", ".", ".", ".", ".", ".", ".", "."],
        [".", ".", ".", ".", ".", ".", ".", "."],
        [".", ".", ".", ".", ".", ".", ".", "."],
        [".", ".", ".", ".", ".", ".", ".", "."],
        [".", ".", ".", ".", ".", ".", ".", "."],
        [".", ".", ".", ".", ".", ".", ".", "."],
        [".", ".", ".", ".", ".", ".", ".", "."],
        [".", ".", ".", ".", "K", ".", ".", "k"],
      ],
    };
    const fetchMock = vi.fn<typeof fetch>().mockResolvedValue(
      jsonResponse(responseBody),
    );
    vi.stubGlobal("fetch", fetchMock);

    await expect(importFEN(FEN)).resolves.toEqual(responseBody);
    expect(fetchMock).toHaveBeenCalledOnce();
    expect(fetchMock).toHaveBeenCalledWith("/api/v1/position/fen", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ fen: FEN }),
    });
  });

  it("throws the FastAPI detail message for an error response", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn<typeof fetch>().mockResolvedValue(
        jsonResponse({ detail: "Invalid board layout" }, 400),
      ),
    );

    await expect(importFEN(FEN)).rejects.toThrow("Invalid board layout");
  });

  it("uses a fallback when an error response has no detail", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn<typeof fetch>().mockResolvedValue(jsonResponse({}, 500)),
    );

    await expect(importFEN(FEN)).rejects.toThrow("FEN import failed");
  });

  it("propagates network errors", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn<typeof fetch>().mockRejectedValue(new Error("Network unavailable")),
    );

    await expect(importFEN(FEN)).rejects.toThrow("Network unavailable");
  });
});
