import React from "react";
import "../styles/ControlPanel.css";

interface ControlPanelProps {
  onReset?: () => void;
  onFlip?: () => void;
  onEngineSettings?: () => void;

  whiteDepth: number;
  blackDepth: number;
  setWhiteDepth: (v: number) => void;
  setBlackDepth: (v: number) => void;

  showEngineSettings: boolean;
}

export const ControlPanel: React.FC<ControlPanelProps> = ({
  onReset,
  onFlip,
  onEngineSettings,
  whiteDepth,
  blackDepth,
  setWhiteDepth,
  setBlackDepth,
  showEngineSettings,
}) => {
  return (
    <div className="control-panel">

      <button className="control-panel-button" onClick={onReset}>
        🔄 Reset
      </button>

      <button className="control-panel-button" onClick={onFlip}>
        🔃 Flip
      </button>

      <button className="control-panel-button" onClick={onEngineSettings}>
        ⚙️ Engine
      </button>
      <button className="control-panel-button" onClick={onEngineSettings}>
        ⚙️ Dummy
      </button>


        <div className={`engine-settings-panel ${showEngineSettings ? "open" : ""}`}>
          <div className="engine-settings-title">Depth</div>

          <div className="engine-slider">
              <label>White: {whiteDepth}</label>
              <input
                type="range"
                min="1"
                max="15"
                value={whiteDepth}
                onChange={(e) => setWhiteDepth(Number(e.target.value))}
              />
          </div>
          <div className="engine-slider">
              <label>Black: {blackDepth}</label>
              <input
                type="range"
                min="1"
                max="15"
                value={blackDepth}
                onChange={(e) => setBlackDepth(Number(e.target.value))}
              />
          </div>
        </div>

    </div>
  );
};