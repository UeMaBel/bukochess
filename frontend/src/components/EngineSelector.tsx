import React from "react";
import type { EngineId } from "../api/engine";

export type PlayerSelection = "human" | EngineId;

interface EngineSelectorProps {
  playerColor: "w" | "b";
  value: PlayerSelection;
  onChange: (val: PlayerSelection) => void;
}

export const EngineSelector: React.FC<EngineSelectorProps> = ({
  playerColor,
  value,
  onChange,
}) => {
  return (
    <div>
      <label>{playerColor === "w" ? "White" : "Black"}: </label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value as PlayerSelection)}
      >
        <option value="human">Human</option>
        <option value="random">Random Engine</option>
        <option value="dumb">Dumb Engine</option>
        <option value="alphabeta">AlphaBeta Engine</option>
      </select>
    </div>
  );
};
