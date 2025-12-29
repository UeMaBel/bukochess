import React from "react";
import { BoardWrapper } from "./components/BoardWrapper";
import { EngineSelector } from "./components/EngineSelector";
import { useGameStore } from "./store/gameStore";

const App: React.FC = () => {
  const { mode, setMode } = useGameStore();

  return (
    <div style={{ padding: 20 }}>
      <h1>BukoChess</h1>
      <BoardWrapper />
    </div>
  );
};

export default App;
