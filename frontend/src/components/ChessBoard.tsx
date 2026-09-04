import type React from "react";

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
const PROMOTION_PIECES = ["q", "r", "b", "n"];

interface PendingPromotion {
  from: string;
  to: string;
}

interface PromotionCoordinates {
  top: number;
  left: number;
}

interface ChessBoardProps {
  fen: string;
  board: string[][];
  activeColor: "w" | "b";
  inCheck: boolean;
  legalMoves: string[];
  selectedSquare: string | null;
  isFlipped: boolean;
  pendingPromotion: PendingPromotion | null;
  promotionCoords: PromotionCoordinates | null;
  onSquareClick: (square: string, event: React.MouseEvent) => void;
  onMove: (move: string) => void;
}

export const ChessBoard: React.FC<ChessBoardProps> = ({
  fen,
  board,
  activeColor,
  inCheck,
  legalMoves,
  selectedSquare,
  isFlipped,
  pendingPromotion,
  promotionCoords,
  onSquareClick,
  onMove,
}) => {
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
                    onClick={(event) => onSquareClick(squareName, event)}
                  >
                    {square !== "." ? PIECE_UNICODE[square] : ""}
                  </div>
                );
              },
            )}
          </div>
        ))}

        {pendingPromotion && promotionCoords && (
          <div
            className="promotion-overlay-floating"
            style={{
              top: promotionCoords.top,
              left: promotionCoords.left,
              flexDirection:
                activeColor === "w" ? "column" : "column-reverse",
            }}
          >
            {PROMOTION_PIECES.map((piece) => (
              <button
                key={piece}
                className={`promotion-btn ${activeColor === "w" ? "piece-white" : "piece-black"}`}
                onClick={(event) => {
                  event.stopPropagation();
                  onMove(`${pendingPromotion.from}${pendingPromotion.to}${piece}`);
                }}
              >
                {PIECE_UNICODE[
                  activeColor === "w" ? piece.toUpperCase() : piece
                ]}
              </button>
            ))}
          </div>
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
