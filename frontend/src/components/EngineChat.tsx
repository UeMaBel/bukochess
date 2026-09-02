import React from "react";
import type { EngineMoveRequest, EngineMoveResponse } from "../api/engine";
import "../styles/EngineChat.css";

interface HumanChatEntry {
  fen: string;
  move: string;
  engine: "Human";
  played_color: "w" | "b";
}

export type EngineChatEntry = (EngineMoveResponse | HumanChatEntry) & {
  timestamp: number;
  retryRequest?: EngineMoveRequest;
};

interface Props {
  entries: EngineChatEntry[];
  onRetry: (request: EngineMoveRequest) => void;
}

export const EngineChat: React.FC<Props> = ({ entries, onRetry }) => {
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
            {entry.engine === "Human"
              ? "Human"
              : entry.metadata.name ?? entry.engine}{" "}
            {entry.move && <>→ {entry.move}</>}
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

          {entry.engine === "LLM" &&
            (entry.metadata.error ? (
              <div className="engine-error">
                <div>{entry.metadata.error.message}</div>
                {entry.retryRequest && (
                  <button
                    type="button"
                    className="engine-retry"
                    onClick={() => onRetry(entry.retryRequest!)}
                  >
                    Retry
                  </button>
                )}
              </div>
            ) : (
              <div>{entry.metadata.explanation}</div>
            ))}
        </div>
      ))}
    </div>
  );
};
