import React, { useEffect, useState, useCallback } from "react";
import { getEngineMove } from "../api/engine";
import type { EngineId, EngineMoveRequest } from "../api/engine";
import type { EngineChatEntry } from "./EngineChat";
import { ChessBoard } from "./ChessBoard";
import { GameSidebar } from "./GameSidebar";
import { GameStatusPanel } from "./GameStatusPanel";
import type { AIPlayerSettings } from "../api/aiSettings";
import { useChessGame } from "../hooks/useChessGame";
import { usePlayerSettings } from "../hooks/usePlayerSettings";
import "../styles/board.css";

function buildEngineMoveRequest(
  fen: string,
  engine: EngineId,
  depth: number,
  aiSettings: AIPlayerSettings,
): EngineMoveRequest {
  switch (engine) {
    case "random":
      return { fen, engine, metadata: {} };
    case "dumb":
      return { fen, engine, metadata: { depth } };
    case "alphabeta":
      return { fen, engine, metadata: { depth } };
    case "llm":
      return { fen, engine, metadata: { ...aiSettings } };
  }
}

export const BoardWrapper: React.FC = () => {
  const {
    position: { fen, board, status, inCheck, activeColor, legalMoves },
    moveHistory,
    historyIndex,
    isViewingHistory,
    playMove,
    syncPosition,
    jumpToHistory,
    goBack,
    goForward,
    resetGame,
  } = useChessGame();
  const {
    settings: playerSettings,
    players,
    depths,
    aiSettings,
    updatePlayer,
    updateDepth,
    setAISettings,
  } = usePlayerSettings();
  const [isFlipped, setIsFlipped] = useState(false);
  const flipBoard = () => {
    setIsFlipped((prev) => !prev);
  };
  const [isEngineThinking, setIsEngineThinking] = useState(false);

  const [engineChat, setEngineChat] = useState<EngineChatEntry[]>([]);

  const resetBoard = async () => {
    await resetGame();
    setEngineChat([]);
  };

  // --- Move Handlers ---
  const handleMoveExecution = async (uci: string) => {
    const response = await playMove(uci);
    if (!response) return;

    setEngineChat((current) => [
      {
        fen: response.fen,
        move: response.move,
        engine: "Human",
        played_color: response.played_color,
        timestamp: Date.now(),
      },
      ...current,
    ]);
  };

  const executeEngineRequest = useCallback(
    async (request: EngineMoveRequest) => {
      setIsEngineThinking(true);
      try {
        const res = await getEngineMove(request);

        setEngineChat((prev) => [
          {
            ...res,
            timestamp: Date.now(),
            retryRequest: res.move === null ? request : undefined,
          },
          ...prev,
        ]);

        if (res.move !== null) {
          await syncPosition(res.fen, res.move);
        }
      } catch (e: unknown) {
        const message = e instanceof Error ? e.message : "Unknown engine error";
        console.error("Engine failed:", message);
      } finally {
        setIsEngineThinking(false);
      }
    },
    [syncPosition],
  );

  const onEngineMove = useCallback(async () => {
    if (isViewingHistory) return;
    const currentSettings = playerSettings[activeColor];
    const currentPlayer = currentSettings.player;
    if (currentPlayer === "human" || status.toLowerCase().includes("mate"))
      return;

    const request = buildEngineMoveRequest(
      fen,
      currentPlayer,
      currentSettings.depth,
      currentSettings.ai,
    );
    await executeEngineRequest(request);
  }, [
    fen,
    activeColor,
    status,
    playerSettings,
    executeEngineRequest,
    isViewingHistory,
  ]);

  useEffect(() => {
    const timer = setTimeout(onEngineMove, 600);
    return () => clearTimeout(timer);
  }, [onEngineMove]);

  return (
    <div className="game-container">
      <GameSidebar
        players={players}
        depths={depths}
        aiSettings={aiSettings}
        chatEntries={engineChat}
        onPlayerChange={updatePlayer}
        onDepthChange={updateDepth}
        onAISettingsChange={setAISettings}
        onReset={resetBoard}
        onFlip={flipBoard}
        onRetry={(request) => {
          if (!isViewingHistory) void executeEngineRequest(request);
        }}
      />

      <div style={{ display: "flex", gap: 20, position: "relative" }}>
        <ChessBoard
          /* Reset transient square and promotion selection when the position changes. */
          key={fen}
          fen={fen}
          board={board}
          activeColor={activeColor}
          inCheck={inCheck}
          legalMoves={legalMoves}
          isFlipped={isFlipped}
          onMove={handleMoveExecution}
        />

        <GameStatusPanel
          status={status}
          inCheck={inCheck}
          isEngineThinking={isEngineThinking}
          moves={moveHistory}
          historyIndex={historyIndex}
          onHistorySelect={jumpToHistory}
          onHistoryBack={goBack}
          onHistoryForward={goForward}
        />
      </div>
    </div>
  );
};
