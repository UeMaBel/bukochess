import type React from "react";
import type { AISettings } from "../api/aiSettings";
import type { EngineMoveRequest } from "../api/engine";
import { ControlPanel } from "./ControlPanel";
import { EngineChat } from "./EngineChat";
import type { EngineChatEntry } from "./EngineChat";
import { EngineSelector } from "./EngineSelector";
import type { PlayerSelection } from "./EngineSelector";

type PlayerColor = "w" | "b";

interface GameSidebarProps {
  players: Record<PlayerColor, PlayerSelection>;
  depths: Record<PlayerColor, number>;
  aiSettings: AISettings;
  settingsVisibility: {
    engine: boolean;
    ai: boolean;
  };
  chatEntries: EngineChatEntry[];
  onPlayerChange: (color: PlayerColor, player: PlayerSelection) => void;
  onDepthChange: (color: PlayerColor, depth: number) => void;
  onAISettingsChange: React.Dispatch<React.SetStateAction<AISettings>>;
  onReset: () => void;
  onFlip: () => void;
  onToggleEngineSettings: () => void;
  onToggleAISettings: () => void;
  onRetry: (request: EngineMoveRequest) => void;
}

export const GameSidebar: React.FC<GameSidebarProps> = ({
  players,
  depths,
  aiSettings,
  settingsVisibility,
  chatEntries,
  onPlayerChange,
  onDepthChange,
  onAISettingsChange,
  onReset,
  onFlip,
  onToggleEngineSettings,
  onToggleAISettings,
  onRetry,
}) => (
  <div className="engine-sidebar">
    <ControlPanel
      onReset={onReset}
      onFlip={onFlip}
      onEngineSettings={onToggleEngineSettings}
      onAISettings={onToggleAISettings}
      whiteDepth={depths.w}
      blackDepth={depths.b}
      setWhiteDepth={(depth) => onDepthChange("w", depth)}
      setBlackDepth={(depth) => onDepthChange("b", depth)}
      aiSettings={aiSettings}
      setAISettings={onAISettingsChange}
      showEngineSettings={settingsVisibility.engine}
      showAISettings={settingsVisibility.ai}
    />

    <h3>🥥 Players</h3>
    <div className="engine-row">
      <EngineSelector
        playerColor="w"
        value={players.w}
        onChange={(player) => onPlayerChange("w", player)}
      />
    </div>
    <div className="engine-row">
      <EngineSelector
        playerColor="b"
        value={players.b}
        onChange={(player) => onPlayerChange("b", player)}
      />
    </div>

    <EngineChat entries={chatEntries} onRetry={onRetry} />
  </div>
);
