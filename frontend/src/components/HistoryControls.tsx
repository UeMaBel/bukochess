import React from "react";
import "../styles/HistoryControls.css";

interface HistoryControlsProps {
  canGoBack: boolean;
  canGoForward: boolean;
  onBack: () => void;
  onForward: () => void;
}

export const HistoryControls: React.FC<HistoryControlsProps> = ({
  canGoBack,
  canGoForward,
  onBack,
  onForward,
}) => {
  return (
    <div className="history-controls">
      <button
        className="history-control-button"
        onClick={onBack}
        disabled={!canGoBack}
      >
        ◀
      </button>

      <button
        className="history-control-button"
        onClick={onForward}
        disabled={!canGoForward}
      >
        ▶
      </button>
    </div>
  );
};