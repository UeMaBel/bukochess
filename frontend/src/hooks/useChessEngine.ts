import { useCallback, useEffect, useState } from "react";
import type { AIPlayerSettings } from "../api/aiSettings";
import { getEngineMove } from "../api/engine";
import type { EngineId, EngineMoveRequest } from "../api/engine";
import type { MoveResponseFast } from "../api/game";
import type { EngineChatEntry } from "../components/EngineChat";
import type { PlayerSettingsByColor } from "./usePlayerSettings";

type BuildEngineMoveRequest = (
  fen: string,
  engine: EngineId,
  depth: number,
  aiSettings: AIPlayerSettings,
) => EngineMoveRequest;

interface UseChessEngineOptions {
  fen: string;
  status: string;
  activeColor: "w" | "b";
  playerSettings: PlayerSettingsByColor;
  isViewingHistory: boolean;
  buildRequest: BuildEngineMoveRequest;
  onEngineMove: (fen: string, move: string) => Promise<void>;
}

export function useChessEngine({
  fen,
  status,
  activeColor,
  playerSettings,
  isViewingHistory,
  buildRequest,
  onEngineMove,
}: UseChessEngineOptions) {
  const [isEngineThinking, setIsEngineThinking] = useState(false);
  const [chatEntries, setChatEntries] = useState<EngineChatEntry[]>([]);

  const executeRequest = useCallback(
    async (request: EngineMoveRequest) => {
      setIsEngineThinking(true);
      try {
        const response = await getEngineMove(request);

        setChatEntries((current) => [
          {
            ...response,
            timestamp: Date.now(),
            retryRequest: response.move === null ? request : undefined,
          },
          ...current,
        ]);

        if (response.move !== null) {
          await onEngineMove(response.fen, response.move);
        }
      } catch (error: unknown) {
        const message =
          error instanceof Error ? error.message : "Unknown engine error";
        console.error("Engine failed:", message);
      } finally {
        setIsEngineThinking(false);
      }
    },
    [onEngineMove],
  );

  const requestEngineMove = useCallback(async () => {
    if (isViewingHistory) return;

    const currentSettings = playerSettings[activeColor];
    if (
      currentSettings.player === "human" ||
      status.toLowerCase().includes("mate")
    ) {
      return;
    }

    const request = buildRequest(
      fen,
      currentSettings.player,
      currentSettings.depth,
      currentSettings.ai,
    );
    await executeRequest(request);
  }, [
    activeColor,
    buildRequest,
    executeRequest,
    fen,
    isViewingHistory,
    playerSettings,
    status,
  ]);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void requestEngineMove();
    }, 600);

    return () => window.clearTimeout(timer);
  }, [requestEngineMove]);

  const recordHumanMove = useCallback((response: MoveResponseFast) => {
    setChatEntries((current) => [
      {
        fen: response.fen,
        move: response.move,
        engine: "Human",
        played_color: response.played_color,
        timestamp: Date.now(),
      },
      ...current,
    ]);
  }, []);

  const clearChat = useCallback(() => setChatEntries([]), []);

  return {
    isEngineThinking,
    chatEntries,
    retry: executeRequest,
    recordHumanMove,
    clearChat,
  };
}
