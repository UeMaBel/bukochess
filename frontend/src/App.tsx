import React from "react";
import { BoardWrapper } from "./components/BoardWrapper";
import { EngineSelector } from "./components/EngineSelector";
import { useGameStore } from "./store/gameStore";

const App: React.FC = () => {
  const { mode, setMode } = useGameStore();

  return (
    <div style={{ padding: 20 }}>
      <h1>BukoChess</h1>
      <div style={{ marginBottom: 10 }}>
        <label>
          Mode:{" "}
          <select value={mode} onChange={(e) => setMode(e.target.value as any)}>
            <option value="human">Human vs Human</option>
            <option value="engine">Human vs Engine</option>
          </select>
        </label>
        {mode === "engine" && <EngineSelector />}
      </div>
      <BoardWrapper />
    </div>
  );
};

export default App;
