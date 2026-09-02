import React from "react";
import type { EngineMoveResponse } from "../api/engine";
import "../styles/EngineChat.css";

interface HumanChatEntry {
  fen: string;
  move: string;
  engine: "Human";
  played_color: "w" | "b";
}

export type EngineChatEntry = (EngineMoveResponse | HumanChatEntry) & {
  timestamp: number;
};

interface Props {
  entries: EngineChatEntry[];
}

export const EngineChat: React.FC<Props> = ({ entries }) => {
  return (
    <div className="engine-chat">
      {entries.map((entry, i) => (
        <div key={i} className="engine-message">
          <div>
            {entry.engine === "Human"
              ? entry.played_color === "w"
                ? "⚪👤"
                : "⚫👤"
              : entry.played_color === "w"
                ? "⚪🤖"
                : "⚫🤖"}{" "}
            {entry.engine === "Human" ? "Human" : entry.metadata.name} →{" "}
            {entry.move}
          </div>

          {entry.engine === "dumb" && (
            <div>
              Eval: {entry.metadata.evaluation.toFixed(2)} | Depth:{" "}
              {entry.metadata.depth}
            </div>
          )}

          {entry.engine === "alphabeta" && (
            <>
              <div>
                Eval: {entry.metadata.evaluation.toFixed(2)} | Depth:{" "}
                {entry.metadata.depth}
              </div>
              <div>
                Nodes: {entry.metadata.nodes.toLocaleString()} | Cutoffs:{" "}
                {entry.metadata.cutoffs.toLocaleString()}
              </div>
              <div>
                TT hits: {entry.metadata.tt_hits.toLocaleString()} | Q-search:{" "}
                {entry.metadata.quiesce_calls.toLocaleString()}
              </div>
            </>
          )}
          {entry.engine === "LLM" && (
            <>
              <div>{entry.metadata.explanation}</div>
            </>
          )}
        </div>
      ))}
    </div>
  );
};
