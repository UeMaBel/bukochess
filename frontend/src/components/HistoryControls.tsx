import React from "react";

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
        onClick={onBack}
        disabled={!canGoBack}
      >
        ◀
      </button>

      <button
        onClick={onForward}
        disabled={!canGoForward}
      >
        ▶
      </button>
    </div>
  );
};