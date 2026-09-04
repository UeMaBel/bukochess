import React from "react";
import { ChessGame } from "./components/ChessGame";

const App: React.FC = () => {
  return (
    <div style={{ padding: 20 }}>
      <h1>BukoChess</h1>
      <ChessGame />
    </div>
  );
};

export default App;
