import React from "react";

interface EngineSelectorProps {
  playerColor: "w" | "b";
  value: string;
  onChange: (val: string) => void;
}

export const EngineSelector: React.FC<EngineSelectorProps> = ({ playerColor, value, onChange }) => {
  return (
    <div>
      <label>{playerColor === "w" ? "White" : "Black"}: </label>
      <select value={value} onChange={(e) => onChange(e.target.value)}>
        <option value="human">Human</option>
        <option value="random">Random Engine</option>
        <option value="dumb">Dumb Engine</option>
        <option value="alphabeta">AlphaBeta Engine</option>
        {/* add more engines later */}
      </select>
    </div>
  );
};
