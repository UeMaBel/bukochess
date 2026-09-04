import React, { useState } from "react";
import type { EngineId, EngineMoveRequest } from "../api/engine";
import { ChessBoard } from "./ChessBoard";
import { GameSidebar } from "./GameSidebar";
import { GameStatusPanel } from "./GameStatusPanel";
import type { AIPlayerSettings } from "../api/aiSettings";
import { useChessGame } from "../hooks/useChessGame";
import { useChessEngine } from "../hooks/useChessEngine";
import { usePlayerSettings } from "../hooks/usePlayerSettings";
import "../styles/ChessGame.css";

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

export const ChessGame: React.FC = () => {
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
  const {
    isEngineThinking,
    chatEntries,
    retry,
    recordHumanMove,
    clearChat,
  } = useChessEngine({
    fen,
    status,
    activeColor,
    playerSettings,
    isViewingHistory,
    buildRequest: buildEngineMoveRequest,
    onEngineMove: syncPosition,
  });
  const [isFlipped, setIsFlipped] = useState(false);
  const flipBoard = () => {
    setIsFlipped((prev) => !prev);
  };
  const resetBoard = async () => {
    await resetGame();
    clearChat();
  };

  // --- Move Handlers ---
  const handleMoveExecution = async (uci: string) => {
    const response = await playMove(uci);
    if (!response) return;
    recordHumanMove(response);
  };

  return (
    <div className="game-container">
      <GameSidebar
        players={players}
        depths={depths}
        aiSettings={aiSettings}
        chatEntries={chatEntries}
        onPlayerChange={updatePlayer}
        onDepthChange={updateDepth}
        onAISettingsChange={setAISettings}
        onReset={resetBoard}
        onFlip={flipBoard}
        onRetry={(request) => {
          if (!isViewingHistory) void retry(request);
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
