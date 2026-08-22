import React, { useEffect, useState, useCallback } from "react";
import { importFEN } from "../api/position";
import { gameStatus, makeMoveFast } from "../api/game";
import { getLegalMoves } from "../api/position";
import { getEngineMove } from "../api/engine";
import type { EngineId, EngineMoveRequest } from "../api/engine";
import { EngineSelector } from "./EngineSelector";
import type { PlayerSelection } from "./EngineSelector";
import { BukoLoader } from "./BukoLoader";
import { HistoryControls } from "./HistoryControls";
import { MoveHistory } from "./MoveHistory";
import { EngineChat } from "./EngineChat";
import type { EngineChatEntry } from "./EngineChat";
import { ControlPanel } from "./ControlPanel";
import "../styles/board.css";

const PIECE_UNICODE: Record<string, string> = {
  p: "♟", r: "♜", n: "♞", b: "♝", q: "♛", k: "♚",
  P: "♙", R: "♖", N: "♘", B: "♗", Q: "♕", K: "♔",
};

const FILES = ["a", "b", "c", "d", "e", "f", "g", "h"];
const RANKS = ["8", "7", "6", "5", "4", "3", "2", "1"];
const START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

function buildEngineMoveRequest(
  fen: string,
  engine: EngineId,
  depth: number
): EngineMoveRequest {
  switch (engine) {
    case "random":
      return { fen, engine, metadata: {} };
    case "dumb":
      return { fen, engine, metadata: { depth } };
    case "alphabeta":
      return { fen, engine, metadata: { depth } };
  }
}

export const BoardWrapper: React.FC = () => {
  const [fen, setFen] = useState(START_FEN);
  const [board, setBoard] = useState<string[][]>([]);
  const [status, setStatus] = useState<string>("");
  const [inCheck, setInCheck] = useState(false);
  const [activeColor, setActiveColor] = useState<"w" | "b">("w");
  const [legalMoves, setLegalMoves] = useState<string[]>([]);
  const [selectedSquare, setSelectedSquare] = useState<string | null>(null);
  const [whitePlayer, setWhitePlayer] = useState<PlayerSelection>("human");
  const [blackPlayer, setBlackPlayer] = useState<PlayerSelection>("random");
  const [isFlipped, setIsFlipped] = useState(false);
  const flipBoard = () => {
    setIsFlipped(prev => !prev);
  };
  const ranksToRender = isFlipped ? [...board].reverse() : board;

  const [pendingPromotion, setPendingPromotion] = useState<{ from: string; to: string } | null>(null);
  const [promotionCoords, setPromotionCoords] = useState<{ top: number; left: number } | null>(null);
  const [isEngineThinking, setIsEngineThinking] = useState(false);

  const [whiteDepth, setWhiteDepth] = useState(4);
  const [blackDepth, setBlackDepth] = useState(4);
  const [showEngineSettings, setShowEngineSettings] = useState(false);

  interface MoveEntry {
  move: string;
  fen: string;
  }

  const [engineChat, setEngineChat] = useState<EngineChatEntry[]>([]);

  const [moveHistory, setMoveHistory] = useState<MoveEntry[]>([
    {
      move: "start",
      fen: START_FEN,
    },
  ]);

  const [historyIndex, setHistoryIndex] = useState<number>(0);

  const isViewingHistory =
    historyIndex < moveHistory.length -1;

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
    setSelectedSquare(null);
    setPendingPromotion(null);

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
        getLegalMoves({ fen: newFen })
      ]);
      setFen(newFen);
      setBoard(boardRes.board);
      setInCheck(statusRes.in_check);
      setActiveColor(statusRes.active_color);
      setStatus(statusRes.status);
      setLegalMoves(movesRes.moves);
      if (move) {
          setMoveHistory(prev => [
            ...prev,
            { move, fen: newFen }
          ]);
          setHistoryIndex(prev => prev + 1);
      }
    } catch (e) {
      console.error("Game state sync failed:", e);
    }
  }, []);

  useEffect(() => { updateGameState(START_FEN); }, [updateGameState]);

  // --- Move Handlers ---
  const handleMoveExecution = async (uci: string) => {
    try {
      if (isViewingHistory) return;
      setSelectedSquare(null);
      setPendingPromotion(null);
      const res = await makeMoveFast(fen, uci);
      // ADD TO CHAT
      setEngineChat(prev => [
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

    } catch (e: any) {
      console.error("Move execution failed:", e.message);
    }
  };

  const onEngineMove = useCallback(async () => {
    if (isViewingHistory) return;
    const currentPlayer = activeColor === "w" ? whitePlayer : blackPlayer;
    if (currentPlayer === "human" || status.toLowerCase().includes("mate")) return;

    setIsEngineThinking(true);
    try {
      const currentDepth = activeColor === "w" ? whiteDepth : blackDepth;
      const request = buildEngineMoveRequest(fen, currentPlayer, currentDepth);
      const res = await getEngineMove(request);

      // ADD TO CHAT
      setEngineChat(prev => [
        {
          ...res,
          timestamp: Date.now(),
        },
        ...prev,
      ]);


      await updateGameState(res.fen, res.move);
    } catch (e: any) {
      console.error("Engine failed:", e.message);
    } finally {
        setIsEngineThinking(false);}

  }, [fen, activeColor, whitePlayer, blackPlayer, whiteDepth, blackDepth, status, updateGameState, isViewingHistory]);

  useEffect(() => {
    const timer = setTimeout(onEngineMove, 600);
    return () => clearTimeout(timer);
  }, [onEngineMove]);

  // --- Click Logic ---
  const onSquareClick = (sq: string, e: React.MouseEvent) => {
    if (pendingPromotion) {
      setPendingPromotion(null);
      return;
    }

    if (!selectedSquare) {
      if (legalMoves.some(m => m.startsWith(sq))) setSelectedSquare(sq);
      return;
    }

    const movePrefix = selectedSquare + sq;
    const pMoves = legalMoves.filter(m => m.startsWith(movePrefix) && m.length === 5);

    if (pMoves.length > 0) {
  const rect = e.currentTarget.getBoundingClientRect();
  const boardRect = e.currentTarget.closest(".chess-board")?.getBoundingClientRect();

  if (boardRect) {
    const squareSize = rect.height;
    const topOffset = rect.top - boardRect.top;

    setPromotionCoords({
      // If White: starts at top (0) and goes down.
      // If Black: starts at bottom (7 squares down), we subtract 3 square-heights
      // so the 4-button menu spans from square 5 to square 8.
      top: activeColor === 'w' ? topOffset : topOffset - (squareSize * 3),
      left: rect.left - boardRect.left,
    });
  }
  setPendingPromotion({ from: selectedSquare, to: sq });
  return;
}

    if (legalMoves.includes(movePrefix)) {
      handleMoveExecution(movePrefix);
    } else {
      setSelectedSquare(legalMoves.some(m => m.startsWith(sq)) ? sq : null);
    }
  };

  // --- Sub-Renders ---
  const renderPromotionModal = () => {
    if (!pendingPromotion || !promotionCoords) return null;
    return (
      <div className="promotion-overlay-floating" style={{
        top: promotionCoords.top,
        left: promotionCoords.left,
        flexDirection: activeColor === 'w' ? 'column' : 'column-reverse'
      }}>
        {['q', 'r', 'b', 'n'].map(p => (
          <button
            key={p}
            className={`promotion-btn ${activeColor === 'w' ? 'piece-white' : 'piece-black'}`}
            onClick={(e) => { e.stopPropagation(); handleMoveExecution(`${pendingPromotion.from}${pendingPromotion.to}${p}`); }}
          >
            {PIECE_UNICODE[activeColor === 'w' ? p.toUpperCase() : p]}
          </button>
        ))}
      </div>
    );
  };

  return (
    <div className="game-container">
      <div className="engine-sidebar">
          <ControlPanel
              onReset={resetBoard}
              onFlip={flipBoard}
              onEngineSettings={() => setShowEngineSettings(v => !v)}

              whiteDepth={whiteDepth}
              blackDepth={blackDepth}
              setWhiteDepth={setWhiteDepth}
              setBlackDepth={setBlackDepth}

              showEngineSettings={showEngineSettings}
          />
        <h3>🥥 Players</h3>
        <div className="engine-row">
          <EngineSelector playerColor="w" value={whitePlayer} onChange={setWhitePlayer} />
        </div>
        <div className="engine-row">
          <EngineSelector playerColor="b" value={blackPlayer} onChange={setBlackPlayer} />
        </div>
        <EngineChat entries={engineChat} />
      </div>

      <div style={{ display: "flex", gap: 20, position: "relative" }}>
        <div className="board-wrapper">
          <div /><div className="file-labels">{FILES.map(f => <div key={f}>{f}</div>)}</div><div />
          <div className="rank-labels">{RANKS.map(r => <div key={r}>{r}</div>)}</div>

          <div className="chess-board" style={{ position: "relative" }}>
              {ranksToRender.map((rank, r) => (
                <div key={r} className="chess-rank"> {/* Re-added the row wrapper */}
                  {(isFlipped ? [...rank].reverse() : rank).map((sq, f) => {
                    const realRank = isFlipped ? r + 1 : 8 - r;
                    const realFile = isFlipped ? FILES[7 - f] : FILES[f];
                    const name = realFile + realRank;
                    const isKing = sq.toLowerCase() === 'k' && (activeColor === "w" ? sq === "K" : sq === "k");
                    const isWhitePiece = sq !== "." && sq === sq.toUpperCase();
                    const isBlackPiece = sq !== "." && sq === sq.toLowerCase();

                    return (
                      <div
                        key={name}
                        className={`chess-square ${(r + f) % 2 === 0 ? "light" : "dark"}
                          ${selectedSquare && legalMoves.some(m => m.startsWith(selectedSquare + name)) ? "legal-target" : ""}
                          ${selectedSquare === name ? "selected" : ""}
                          ${isWhitePiece ? "piece-white" : ""}
                          ${isBlackPiece ? "piece-black" : ""}
                          ${inCheck && isKing ? "check" : ""}`}
                        onClick={(e) => onSquareClick(name, e)}
                      >
                        {sq !== "." ? PIECE_UNICODE[sq] : ""}
                      </div>
                    );
                  })}
                </div>
              ))}
              {renderPromotionModal()}
            </div>

          <div className="rank-labels">
              {(isFlipped ? [...RANKS].reverse() : RANKS).map(r => (
                <div key={r}>{r}</div>
              ))}
          </div>
          <div />
          <div className="file-labels">
              {(isFlipped ? [...FILES].reverse() : FILES).map(f => (
                <div key={f}>{f}</div>
              ))}
          </div>
          <div />
          <div className="fen-container-wide">
        <label>Current FEN Position</label>
        <textarea
          value={fen}
          rows={2}
          readOnly
          onClick={(e) => (e.target as HTMLTextAreaElement).select()}
        />
      </div>
        </div>

        <div className="game-status-panel">
            <div>
              <h3>🥥 Status</h3>

              {isEngineThinking ? (
                <BukoLoader />
              ) : (
                <div className="status-text">{status}</div>
              )}


              <MoveHistory
                moves={moveHistory}
                currentIndex={historyIndex}
                onSelect={jumpToHistory}
              />

              <HistoryControls
                canGoBack={historyIndex > 0}
                canGoForward={historyIndex < moveHistory.length - 1}
                onBack={goBack}
                onForward={goForward}
              />
            </div>


          <div className={`check-text ${inCheck ? "visible" : ""}`} style={{ color: "red", fontWeight: "bold" }}>
            {inCheck ? "CHECK!" : ""}
          </div>
        </div>
      </div>
    </div>

  );
};