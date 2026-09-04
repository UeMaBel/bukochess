import React, { useEffect, useState, useCallback } from "react";
import { importFEN } from "../api/position";
import { gameStatus, makeMoveFast } from "../api/game";
import { getLegalMoves } from "../api/position";
import { getEngineMove } from "../api/engine";
import type { EngineId, EngineMoveRequest } from "../api/engine";
import type { PlayerSelection } from "./EngineSelector";
import type { MoveEntry } from "./MoveHistory";
import type { EngineChatEntry } from "./EngineChat";
import { ChessBoard } from "./ChessBoard";
import { GameSidebar } from "./GameSidebar";
import { GameStatusPanel } from "./GameStatusPanel";
import { DEFAULT_AI_SETTINGS } from "../api/aiSettings";
import type { AISettings, AIPlayerSettings } from "../api/aiSettings";
import "../styles/board.css";

const START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

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
  const [fen, setFen] = useState(START_FEN);
  const [board, setBoard] = useState<string[][]>([]);
  const [status, setStatus] = useState<string>("");
  const [inCheck, setInCheck] = useState(false);
  const [activeColor, setActiveColor] = useState<"w" | "b">("w");
  const [legalMoves, setLegalMoves] = useState<string[]>([]);
  const [whitePlayer, setWhitePlayer] = useState<PlayerSelection>("human");
  const [blackPlayer, setBlackPlayer] = useState<PlayerSelection>("random");
  const [isFlipped, setIsFlipped] = useState(false);
  const flipBoard = () => {
    setIsFlipped((prev) => !prev);
  };
  const [isEngineThinking, setIsEngineThinking] = useState(false);

  const [whiteDepth, setWhiteDepth] = useState(4);
  const [blackDepth, setBlackDepth] = useState(4);
  const [showEngineSettings, setShowEngineSettings] = useState(false);
  const [showAISettings, setShowAISettings] = useState(false);
  const [aiSettings, setAISettings] = useState<AISettings>(DEFAULT_AI_SETTINGS);

  const [engineChat, setEngineChat] = useState<EngineChatEntry[]>([]);

  const [moveHistory, setMoveHistory] = useState<MoveEntry[]>([
    {
      move: "start",
      fen: START_FEN,
    },
  ]);

  const [historyIndex, setHistoryIndex] = useState<number>(0);

  const isViewingHistory = historyIndex < moveHistory.length - 1;

  const jumpToHistory = async (index: number) => {
    if (index < 0 || index >= moveHistory.length) return;

    setHistoryIndex(index);

    await updateGameState(moveHistory[index].fen);
  };
  const goBack = () => {
    jumpToHistory(historyIndex - 1);
  };

  const goForward = () => {
    jumpToHistory(historyIndex + 1);
  };

  const resetBoard = async () => {
    setMoveHistory([
      {
        move: "start",
        fen: START_FEN,
      },
    ]);

    setHistoryIndex(0);
    await updateGameState(START_FEN);
    setEngineChat([]);
  };

  // --- State Sync ---
  const updateGameState = useCallback(async (newFen: string, move?: string) => {
    try {
      const [boardRes, statusRes, movesRes] = await Promise.all([
        importFEN(newFen),
        gameStatus({ fen: newFen }),
        getLegalMoves({ fen: newFen }),
      ]);
      setFen(newFen);
      setBoard(boardRes.board);
      setInCheck(statusRes.in_check);
      setActiveColor(statusRes.active_color);
      setStatus(statusRes.status);
      setLegalMoves(movesRes.moves);
      if (move) {
        setMoveHistory((prev) => [...prev, { move, fen: newFen }]);
        setHistoryIndex((prev) => prev + 1);
      }
    } catch (e) {
      console.error("Game state sync failed:", e);
    }
  }, []);

  useEffect(() => {
    updateGameState(START_FEN);
  }, [updateGameState]);

  // --- Move Handlers ---
  const handleMoveExecution = async (uci: string) => {
    try {
      if (isViewingHistory) return;
      const res = await makeMoveFast(fen, uci);
      // ADD TO CHAT
      setEngineChat((prev) => [
        {
          fen: res.fen,
          move: res.move,
          engine: "Human",
          played_color: res.played_color === "w" ? "w" : "b",
          timestamp: Date.now(),
        },
        ...prev,
      ]);
      setFen(res.fen);
      await updateGameState(res.fen, uci);
    } catch (e: unknown) {
      const message = e instanceof Error ? e.message : "Unknown move error";
      console.error("Move execution failed:", message);
    }
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
          await updateGameState(res.fen, res.move);
        }
      } catch (e: unknown) {
        const message = e instanceof Error ? e.message : "Unknown engine error";
        console.error("Engine failed:", message);
      } finally {
        setIsEngineThinking(false);
      }
    },
    [updateGameState],
  );

  const onEngineMove = useCallback(async () => {
    if (isViewingHistory) return;
    const currentPlayer = activeColor === "w" ? whitePlayer : blackPlayer;
    if (currentPlayer === "human" || status.toLowerCase().includes("mate"))
      return;

    const currentDepth = activeColor === "w" ? whiteDepth : blackDepth;
    const currentAiSettings =
      activeColor === "w" ? aiSettings.white : aiSettings.black;
    const request = buildEngineMoveRequest(
      fen,
      currentPlayer,
      currentDepth,
      currentAiSettings,
    );
    await executeEngineRequest(request);
  }, [
    fen,
    activeColor,
    whitePlayer,
    blackPlayer,
    whiteDepth,
    blackDepth,
    status,
    aiSettings,
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
        players={{ w: whitePlayer, b: blackPlayer }}
        depths={{ w: whiteDepth, b: blackDepth }}
        aiSettings={aiSettings}
        settingsVisibility={{
          engine: showEngineSettings,
          ai: showAISettings,
        }}
        chatEntries={engineChat}
        onPlayerChange={(color, player) => {
          if (color === "w") setWhitePlayer(player);
          else setBlackPlayer(player);
        }}
        onDepthChange={(color, depth) => {
          if (color === "w") setWhiteDepth(depth);
          else setBlackDepth(depth);
        }}
        onAISettingsChange={setAISettings}
        onReset={resetBoard}
        onFlip={flipBoard}
        onToggleEngineSettings={() => setShowEngineSettings((value) => !value)}
        onToggleAISettings={() => setShowAISettings((value) => !value)}
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
