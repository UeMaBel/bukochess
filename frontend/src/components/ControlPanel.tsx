import React from "react";
import "../styles/ControlPanel.css";

interface ControlPanelProps {
  onReset?: () => void;
  onFlip?: () => void;
  onEngineSettings?: () => void;
  onAnalysis?: () => void;
}

export const ControlPanel: React.FC<ControlPanelProps> = ({
  onReset,
  onFlip,
  onEngineSettings,
  onAnalysis,
}) => {
  return (
    <div className="control-panel">
      <button
        className="control-panel-button"
        onClick={onReset}
      >
        🔄 Reset
      </button>

      <button
        className="control-panel-button"
        onClick={onFlip}
      >
        🔃 Flip
      </button>

      <button
        className="control-panel-button"
        onClick={onEngineSettings}
      >
        ⚙️ Engine
      </button>

      <button
        className="control-panel-button"
        onClick={onAnalysis}
      >
        📊 Analysis
      </button>
    </div>
  );
};