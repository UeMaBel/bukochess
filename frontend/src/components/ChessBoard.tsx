import React, { useState } from "react";
import { PromotionPicker } from "./PromotionPicker";

const PIECE_UNICODE: Record<string, string> = {
  p: "\u265f",
  r: "\u265c",
  n: "\u265e",
  b: "\u265d",
  q: "\u265b",
  k: "\u265a",
  P: "\u2659",
  R: "\u2656",
  N: "\u2658",
  B: "\u2657",
  Q: "\u2655",
  K: "\u2654",
};

const FILES = ["a", "b", "c", "d", "e", "f", "g", "h"];
const RANKS = ["8", "7", "6", "5", "4", "3", "2", "1"];
interface ChessBoardProps {
  fen: string;
  board: string[][];
  activeColor: "w" | "b";
  inCheck: boolean;
  legalMoves: string[];
  isFlipped: boolean;
  onMove: (move: string) => void;
}

export const ChessBoard: React.FC<ChessBoardProps> = ({
  fen,
  board,
  activeColor,
  inCheck,
  legalMoves,
  isFlipped,
  onMove,
}) => {
  const [selectedSquare, setSelectedSquare] = useState<string | null>(null);
  const [pendingPromotion, setPendingPromotion] = useState<{
    from: string;
    to: string;
  } | null>(null);
  const [promotionCoords, setPromotionCoords] = useState<{
    top: number;
    left: number;
  } | null>(null);

  const submitMove = (move: string) => {
    setSelectedSquare(null);
    setPendingPromotion(null);
    setPromotionCoords(null);
    onMove(move);
  };

  const handleSquareClick = (
    square: string,
    event: React.MouseEvent<HTMLDivElement>,
  ) => {
    if (pendingPromotion) {
      setPendingPromotion(null);
      setPromotionCoords(null);
      return;
    }

    if (!selectedSquare) {
      if (legalMoves.some((move) => move.startsWith(square))) {
        setSelectedSquare(square);
      }
      return;
    }

    const movePrefix = selectedSquare + square;
    const promotionMoves = legalMoves.filter(
      (move) => move.startsWith(movePrefix) && move.length === 5,
    );

    if (promotionMoves.length > 0) {
      const squareRect = event.currentTarget.getBoundingClientRect();
      const boardRect = event.currentTarget
        .closest(".chess-board")
        ?.getBoundingClientRect();

      if (boardRect) {
        const topOffset = squareRect.top - boardRect.top;
        setPromotionCoords({
          top:
            activeColor === "w"
              ? topOffset
              : topOffset - squareRect.height * 3,
          left: squareRect.left - boardRect.left,
        });
      }
      setPendingPromotion({ from: selectedSquare, to: square });
      return;
    }

    if (legalMoves.includes(movePrefix)) {
      submitMove(movePrefix);
      return;
    }

    setSelectedSquare(
      legalMoves.some((move) => move.startsWith(square)) ? square : null,
    );
  };

  const ranksToRender = isFlipped ? [...board].reverse() : board;
  const filesToRender = isFlipped ? [...FILES].reverse() : FILES;
  const rankLabelsToRender = isFlipped ? [...RANKS].reverse() : RANKS;

  return (
    <div className="board-wrapper">
      <div />
      <div className="file-labels">
        {FILES.map((file) => (
          <div key={file}>{file}</div>
        ))}
      </div>
      <div />

      <div className="rank-labels">
        {RANKS.map((rank) => (
          <div key={rank}>{rank}</div>
        ))}
      </div>

      <div className="chess-board" style={{ position: "relative" }}>
        {ranksToRender.map((rank, rankIndex) => (
          <div key={rankIndex} className="chess-rank">
            {(isFlipped ? [...rank].reverse() : rank).map(
              (square, fileIndex) => {
                const realRank = isFlipped ? rankIndex + 1 : 8 - rankIndex;
                const realFile = isFlipped
                  ? FILES[7 - fileIndex]
                  : FILES[fileIndex];
                const squareName = realFile + realRank;
                const isKingInCheck =
                  square.toLowerCase() === "k" &&
                  (activeColor === "w" ? square === "K" : square === "k");
                const isWhitePiece =
                  square !== "." && square === square.toUpperCase();
                const isBlackPiece =
                  square !== "." && square === square.toLowerCase();
                const isLegalTarget =
                  selectedSquare !== null &&
                  legalMoves.some((move) =>
                    move.startsWith(selectedSquare + squareName),
                  );

                return (
                  <div
                    key={squareName}
                    className={`chess-square ${(rankIndex + fileIndex) % 2 === 0 ? "light" : "dark"}
                      ${isLegalTarget ? "legal-target" : ""}
                      ${selectedSquare === squareName ? "selected" : ""}
                      ${isWhitePiece ? "piece-white" : ""}
                      ${isBlackPiece ? "piece-black" : ""}
                      ${inCheck && isKingInCheck ? "check" : ""}`}
                    onClick={(event) =>
                      handleSquareClick(squareName, event)
                    }
                  >
                    {square !== "." ? PIECE_UNICODE[square] : ""}
                  </div>
                );
              },
            )}
          </div>
        ))}

        {pendingPromotion && promotionCoords && (
          <PromotionPicker
            color={activeColor}
            top={promotionCoords.top}
            left={promotionCoords.left}
            onSelect={(piece) =>
              submitMove(
                `${pendingPromotion.from}${pendingPromotion.to}${piece}`,
              )
            }
          />
        )}
      </div>

      <div className="rank-labels">
        {rankLabelsToRender.map((rank) => (
          <div key={rank}>{rank}</div>
        ))}
      </div>
      <div />
      <div className="file-labels">
        {filesToRender.map((file) => (
          <div key={file}>{file}</div>
        ))}
      </div>
      <div />

      <div className="fen-container-wide">
        <label>Current FEN Position</label>
        <textarea
          value={fen}
          rows={2}
          readOnly
          onClick={(event) => event.currentTarget.select()}
        />
      </div>
    </div>
  );
};
