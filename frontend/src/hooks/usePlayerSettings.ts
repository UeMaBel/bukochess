import { useCallback, useState } from "react";
import type { Dispatch, SetStateAction } from "react";
import { DEFAULT_AI_SETTINGS } from "../api/aiSettings";
import type { AIPlayerSettings, AISettings } from "../api/aiSettings";
import type { PlayerSelection } from "../components/EngineSelector";

type PlayerColor = "w" | "b";

export interface PlayerSettings {
  player: PlayerSelection;
  depth: number;
  ai: AIPlayerSettings;
}

export type PlayerSettingsByColor = Record<PlayerColor, PlayerSettings>;

const INITIAL_PLAYER_SETTINGS: PlayerSettingsByColor = {
  w: {
    player: "human",
    depth: 4,
    ai: { ...DEFAULT_AI_SETTINGS.white },
  },
  b: {
    player: "random",
    depth: 4,
    ai: { ...DEFAULT_AI_SETTINGS.black },
  },
};

export function usePlayerSettings() {
  const [settings, setSettings] = useState<PlayerSettingsByColor>(
    INITIAL_PLAYER_SETTINGS,
  );

  const updatePlayer = useCallback(
    (color: PlayerColor, player: PlayerSelection) => {
      setSettings((current) => ({
        ...current,
        [color]: { ...current[color], player },
      }));
    },
    [],
  );

  const updateDepth = useCallback((color: PlayerColor, depth: number) => {
    setSettings((current) => ({
      ...current,
      [color]: { ...current[color], depth },
    }));
  }, []);

  const setAISettings: Dispatch<SetStateAction<AISettings>> = useCallback(
    (update) => {
      setSettings((current) => {
        const currentAISettings: AISettings = {
          white: current.w.ai,
          black: current.b.ai,
        };
        const nextAISettings =
          typeof update === "function" ? update(currentAISettings) : update;

        return {
          w: { ...current.w, ai: nextAISettings.white },
          b: { ...current.b, ai: nextAISettings.black },
        };
      });
    },
    [],
  );

  return {
    settings,
    players: {
      w: settings.w.player,
      b: settings.b.player,
    },
    depths: {
      w: settings.w.depth,
      b: settings.b.depth,
    },
    aiSettings: {
      white: settings.w.ai,
      black: settings.b.ai,
    },
    updatePlayer,
    updateDepth,
    setAISettings,
  };
}
