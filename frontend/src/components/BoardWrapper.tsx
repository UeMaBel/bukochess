// frontend/src/components/BoardWrapper.tsx
import React, { useEffect, useState } from "react";

import { importFEN } from "../api/position";
import { makeMove } from "../api/game";
import { gameStatus } from "../api/game";
import { getLegalMoves } from "../api/position";

import { getEngineMove } from "../api/engine";
import { useGameStore } from "../store/gameStore";
import { EngineSelector } from "./EngineSelector";
import "../styles/board.css";


const START_FEN =
  "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

export const BoardWrapper: React.FC = () => {
  const { engine, vsEngine } = useGameStore();

  const [fen, setFen] = useState(START_FEN);
  const [board, setBoard] = useState<string[][]>([]);
  const [status, setStatus] = useState<string>("");
  const [moveInput, setMoveInput] = useState("");
  const files = ["a","b","c","d","e","f","g","h"];
    const ranks = ["8","7","6","5","4","3","2","1"];
    const [error, setError] = useState<string | null>(null);
const [shake, setShake] = useState(false);
const [dragFrom, setDragFrom] = useState<string | null>(null);
const [inCheck, setInCheck] = useState(false);
const [activeColor, setActiveColor] = useState<"w" | "b">("w");
const isKing = (sq: string) =>
  sq === (activeColor === "w" ? "K" : "k");
const [legalMoves, setLegalMoves] = useState<string[]>([]);

const [selectedSquare, setSelectedSquare] = useState<string | null>(null);
const [premove, setPremove] = useState<string | null>(null);



useEffect(() => {
  if (!fen) return;

  gameStatus({ fen }).then((res) => {
    setInCheck(res.in_check);
    setActiveColor(res.active_color);
  });
  // fetch legal moves for current position
  getLegalMoves({ fen }).then((res) => {
    setLegalMoves(res.moves);
  });
}, [fen]);

const movesFrom = (sq: string) =>
  legalMoves.filter(m => m.startsWith(sq));
const squareName = (r: number, f: number) =>
  files[f] + (8 - r);


const onSquareClick = (sq: string) => {
  // selecting source
  if (!selectedSquare) {
    if (movesFrom(sq).length > 0) {
      setSelectedSquare(sq);
    }
    return;
  }

  const move = selectedSquare + sq;

  // legal → play immediately
  if (legalMoves.includes(move)) {
    onUserMove(move);
    setSelectedSquare(null);
    return;
  }

  // illegal → clear selection
  setSelectedSquare(null);
};

  // load board from FEN
  useEffect(() => {
    importFEN(fen).then((res) => setBoard(res.board));
  }, [fen]);

  // user makes a move (uci: e2e4)
const onUserMove = async (uci: string) => {
  try {
    setError(null);
    const res = await makeMove(fen, uci);
    setFen(res.fen);
    setStatus(res.status);
  } catch (e: any) {
    setError(e.message);
    setShake(true);

    setTimeout(() => setShake(false), 300);
    setTimeout(() => setError(null), 2000);
  }
};

const renderBoard = () => (
  <div className="chess-board">
    {board.map((rank, r) => (
      <div key={r} className="chess-rank">
        {rank.map((sq, f) => {
          const square = squareName(r, f);
          const isTarget =
            selectedSquare &&
            legalMoves.includes(selectedSquare + square);

          return (
            <div
              key={f}
              className={`chess-square
                ${(r + f) % 2 === 0 ? "light" : "dark"}
                ${isTarget ? "legal-target" : ""}
              `}
              onClick={() => onSquareClick(square)}
              draggable={sq !== "."}
            >
              {sq}
            </div>
          );
        })}
      </div>
    ))}
  </div>
);

  const renderBoardoo = () => (

  <div className="chess-board">
    {board.map((rank, r) => (
      <div key={r} className="chess-rank">
        {rank.map((sq, f) => (
          <div
            key={f}
          className={`chess-square ${(r + f) % 2 === 0 ? "light" : "dark"}
          ${isTarget ? "legal-target" : ""}
          ${inCheck && isKing(sq) ? "check" : ""}
          `}
          draggable={sq !== "."}
          onClick={() => onSquareClick(squareName(r, f))}
          onDragStart={() => setDragFrom(squareName(r, f))}
          onDragOver={(e) => e.preventDefault()}
          onDrop={() => {
            if (!dragFrom) return;
            const to = squareName(r, f);
            onUserMove(dragFrom + to);
            setDragFrom(null);
          }}
          >
            {sq}
          </div>
        ))}
      </div>
    ))}
  </div>
);

    const renderWrappedBoard=()=> (

    <div className="board-wrapper">
      <div /> {/* top-left empty */}
      <div className="file-labels">
        {files.map(f => <div key={f}>{f}</div>)}
      </div>
      <div />

      <div className="rank-labels">
        {ranks.map(r => <div key={r}>{r}</div>)}
      </div>

      {renderBoard()}

      <div className="rank-labels">
        {ranks.map(r => <div key={r}>{r}</div>)}
      </div>

      <div />
      <div className="file-labels">
        {files.map(f => <div key={f}>{f}</div>)}
      </div>
      <div />
    </div>

    );


  return (
    <div style={{ display: "flex", gap: 16 }}>
      <div>
        <EngineSelector />
        {renderWrappedBoard()}
      </div>

      <div>
        <div>Status: {status}</div>
        <textarea
          value={fen}
          onChange={(e) => setFen(e.target.value)}
          rows={4}
          cols={40}
        />
        <div>
          <input
                className={shake ? "shake" : ""}
              type="text"
              placeholder="e2e4"
              onKeyDown={(e) => {
                const input = e.target as HTMLInputElement;
                if (e.key === "Enter" && input.value.length === 4) {
                  onUserMove(input.value);
                  input.value = "";
                }
              }}
            />

        </div>
      </div>
      {error && (
      <div className="error-message fade" style={{ color: "red", marginTop: 8 }}>
        {error}
      </div>
    )}
    </div>
  );
};
