import React from "react";
import { ChessGame } from "./components/ChessGame";

const App: React.FC = () => {
  return (
    <div className="app">
      <h1 className="app-title">BukoChess</h1>
      <ChessGame />
    </div>
  );
};

export default App;
