import React from "react";

export interface EngineChatEntry {
  move: string;
  fen: string;
  evaluation: number;
  depth: number;
  nodes: number;
  nps: number;
  pv: string[];
  engine: string;
  timestamp: number;
  color: "w" | "b";
}

interface Props {
  entries: EngineChatEntry[];
}

export const EngineChat: React.FC<Props> = ({ entries }) => {
  return (
    <div className="engine-chat">
      {entries.map((e, i) => (
        <div key={i} className="engine-message">
          <div>
            {e.played_color === "w" ? "⚪🤖" : "⚫🤖"} {e.engine} → {e.move}
          </div>

          <div>
            Eval: {e.evaluation.toFixed(2)} | Depth: {e.depth}
          </div>

          <div>
            PV: {e.pv.join(" ")}
          </div>
        </div>
      ))}
    </div>
  );
};