// frontend/src/components/BoardWrapper.tsx
import React, { useEffect, useState } from "react";

import { importFEN } from "../api/position";
import { makeMove } from "../api/game";
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


  // load board from FEN
  useEffect(() => {
    importFEN(fen).then((res) => setBoard(res.board));
  }, [fen]);

  // user makes a move (uci: e2e4)
  const onUserMove = async (uci: string) => {
    const res = await makeMove(fen, uci);
    setFen(res.fen);
    setStatus(res.status);

    if (vsEngine && res.status === "ongoing") {
      const eng = await getEngineMove(res.fen, engine);
      setFen(eng.fen);
      setStatus(eng.status);
    }
  };

  const renderBoard = () => (

  <div className="chess-board">
    {board.map((rank, r) => (
      <div key={r} className="chess-rank">
        {rank.map((sq, f) => (
          <div
            key={f}
            className={`chess-square ${
              (r + f) % 2 === 0 ? "light" : "dark"
            }`}
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
    </div>
  );
};
