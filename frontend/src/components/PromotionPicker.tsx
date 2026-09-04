const PROMOTION_PIECES = ["q", "r", "b", "n"] as const;

export type PromotionPiece = (typeof PROMOTION_PIECES)[number];

const WHITE_PIECES: Record<PromotionPiece, string> = {
  q: "\u2655",
  r: "\u2656",
  b: "\u2657",
  n: "\u2658",
};

const BLACK_PIECES: Record<PromotionPiece, string> = {
  q: "\u265b",
  r: "\u265c",
  b: "\u265d",
  n: "\u265e",
};

interface PromotionPickerProps {
  color: "w" | "b";
  top: number;
  left: number;
  onSelect: (piece: PromotionPiece) => void;
}

export const PromotionPicker: React.FC<PromotionPickerProps> = ({
  color,
  top,
  left,
  onSelect,
}) => {
  const pieces = color === "w" ? WHITE_PIECES : BLACK_PIECES;

  return (
    <div
      className="promotion-overlay-floating"
      style={{
        top,
        left,
        flexDirection: color === "w" ? "column" : "column-reverse",
      }}
    >
      {PROMOTION_PIECES.map((piece) => (
        <button
          key={piece}
          className={`promotion-btn ${color === "w" ? "piece-white" : "piece-black"}`}
          onClick={(event) => {
            event.stopPropagation();
            onSelect(piece);
          }}
        >
          {pieces[piece]}
        </button>
      ))}
    </div>
  );
};
