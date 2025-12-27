import React from "react";
import { useGameStore } from "../store/gameStore";

export const EngineSelector: React.FC = () => {
  const { engine, setEngine } = useGameStore();
  return (
    <select value={engine} onChange={(e) => setEngine(e.target.value as string)}>
      <option value="random">Random</option>
      {/* add more engines later */}
    </select>
  );
};
