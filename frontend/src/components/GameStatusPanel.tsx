import { BukoLoader } from "./BukoLoader";
import { HistoryControls } from "./HistoryControls";
import { MoveHistory } from "./MoveHistory";
import type { MoveEntry } from "./MoveHistory";

interface GameStatusPanelProps {
  status: string;
  inCheck: boolean;
  isEngineThinking: boolean;
  moves: MoveEntry[];
  historyIndex: number;
  onHistorySelect: (index: number) => void;
  onHistoryBack: () => void;
  onHistoryForward: () => void;
}

export const GameStatusPanel: React.FC<GameStatusPanelProps> = ({
  status,
  inCheck,
  isEngineThinking,
  moves,
  historyIndex,
  onHistorySelect,
  onHistoryBack,
  onHistoryForward,
}) => (
  <div className="game-status-panel">
    <div>
      <h3>🥥 Status</h3>

      {isEngineThinking ? (
        <BukoLoader />
      ) : (
        <div className="status-text">{status}</div>
      )}

      <MoveHistory
        moves={moves}
        currentIndex={historyIndex}
        onSelect={onHistorySelect}
      />

      <HistoryControls
        canGoBack={historyIndex > 0}
        canGoForward={historyIndex < moves.length - 1}
        onBack={onHistoryBack}
        onForward={onHistoryForward}
      />
    </div>

    <div
      className={`check-text ${inCheck ? "visible" : ""}`}
      style={{ color: "red", fontWeight: "bold" }}
    >
      {inCheck ? "CHECK!" : ""}
    </div>
  </div>
);
