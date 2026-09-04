import React from "react";
import type { MoveEntry } from "../hooks/useChessGame";

interface MoveHistoryProps {
  moves: MoveEntry[];
  currentIndex: number;
  onSelect: (index: number) => void;
}

export const MoveHistory: React.FC<MoveHistoryProps> = ({
  moves,
  currentIndex,
  onSelect,
}) => {
  const groupedMoves: { white?: MoveEntry; black?: MoveEntry }[] = [];

  for (let i = 1; i < moves.length; i++) {
    const ii=i-1;
    const move = moves[i];

    const pairIndex = Math.floor(ii / 2);

    if (!groupedMoves[pairIndex]) {
      groupedMoves[pairIndex] = {};
    }

    if (ii % 2 === 0) {
      groupedMoves[pairIndex].white = move;
    } else {
      groupedMoves[pairIndex].black = move;
    }
  }

  return (
    <div className="move-history">
    <h4>History</h4>
    <div className="move-history-rows">

      {groupedMoves.map((pair, idx) => {
        const whiteIndex = idx * 2;
        const blackIndex = idx * 2 + 1;

        return (
          <div key={idx} className="history-row">

            <span className="move-number">{idx + 1}.</span>

            <span
              className={`history-move ${
                whiteIndex === currentIndex-1 ? "active" : ""
              }`}
              onClick={() => pair.white && onSelect(whiteIndex+1)}
            >
              {pair.white?.move ?? ""}
            </span>

            <span
              className={`history-move ${
                blackIndex === currentIndex-1 ? "active" : ""
              }`}
              onClick={() => pair.black && onSelect(blackIndex+1)}
            >
             {pair.black?.move ?? ""}
            </span>
          </div>
        );
      })}
    </div></div>
  );
};
