import { useCallback, useEffect, useState } from "react";
import { gameStatus, makeMoveFast } from "../api/game";
import type { MoveResponseFast } from "../api/game";
import { getLegalMoves, importFEN } from "../api/position";

export const START_FEN =
  "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

export interface MoveEntry {
  move: string;
  fen: string;
}

interface ChessPosition {
  fen: string;
  board: string[][];
  status: string;
  inCheck: boolean;
  activeColor: "w" | "b";
  legalMoves: string[];
}

const INITIAL_POSITION: ChessPosition = {
  fen: START_FEN,
  board: [],
  status: "",
  inCheck: false,
  activeColor: "w",
  legalMoves: [],
};

const INITIAL_HISTORY: MoveEntry[] = [{ move: "start", fen: START_FEN }];

async function loadPosition(fen: string): Promise<ChessPosition> {
  const [boardResponse, statusResponse, movesResponse] = await Promise.all([
    importFEN(fen),
    gameStatus({ fen }),
    getLegalMoves({ fen }),
  ]);

  return {
    fen,
    board: boardResponse.board,
    status: statusResponse.status,
    inCheck: statusResponse.in_check,
    activeColor: statusResponse.active_color,
    legalMoves: movesResponse.moves,
  };
}

export function useChessGame() {
  const [position, setPosition] = useState<ChessPosition>(INITIAL_POSITION);
  const [moveHistory, setMoveHistory] =
    useState<MoveEntry[]>(INITIAL_HISTORY);
  const [historyIndex, setHistoryIndex] = useState(0);

  const isViewingHistory = historyIndex < moveHistory.length - 1;

  const syncPosition = useCallback(async (fen: string, move?: string) => {
    try {
      setPosition(await loadPosition(fen));

      if (move) {
        setMoveHistory((current) => [...current, { move, fen }]);
        setHistoryIndex((current) => current + 1);
      }
    } catch (error) {
      console.error("Game state sync failed:", error);
    }
  }, []);

  useEffect(() => {
    let ignoreResult = false;

    void loadPosition(START_FEN)
      .then((initialPosition) => {
        if (!ignoreResult) setPosition(initialPosition);
      })
      .catch((error: unknown) => {
        console.error("Game state sync failed:", error);
      });

    return () => {
      ignoreResult = true;
    };
  }, []);

  const playMove = async (move: string): Promise<MoveResponseFast | null> => {
    if (isViewingHistory) return null;

    try {
      const response = await makeMoveFast(position.fen, move);
      await syncPosition(response.fen, move);
      return response;
    } catch (error: unknown) {
      const message =
        error instanceof Error ? error.message : "Unknown move error";
      console.error("Move execution failed:", message);
      return null;
    }
  };

  const jumpToHistory = async (index: number) => {
    if (index < 0 || index >= moveHistory.length) return;

    setHistoryIndex(index);
    await syncPosition(moveHistory[index].fen);
  };

  const goBack = () => jumpToHistory(historyIndex - 1);
  const goForward = () => jumpToHistory(historyIndex + 1);

  const resetGame = async () => {
    setMoveHistory(INITIAL_HISTORY);
    setHistoryIndex(0);
    await syncPosition(START_FEN);
  };

  return {
    position,
    moveHistory,
    historyIndex,
    isViewingHistory,
    playMove,
    syncPosition,
    jumpToHistory,
    goBack,
    goForward,
    resetGame,
  };
}
