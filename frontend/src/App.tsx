import React from "react";
import { BoardWrapper } from "./components/BoardWrapper";

const App: React.FC = () => {
  return (
    <div style={{ padding: 20 }}>
      <h1>BukoChess</h1>
      <BoardWrapper />
    </div>
  );
};

export default App;
