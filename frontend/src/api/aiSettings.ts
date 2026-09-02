export type AIProvider = "openai" | "anthropic";

export type AIReasoningEffort = "low" | "medium" | "high";
export type AITemperature = 0 | 0.2 | 0.5 | 0.8 | 1;
export type AIMaxOutputTokens = 32 | 64 | 128 | 256 | 8192;
export type AIColor = "white" | "black";

export interface AIModelOption {
  id: string;
  name: string;
  tier: "Cheapest" | "Balanced" | "Best";
}

export interface AIPlayerSettings {
  provider: AIProvider;
  model: string;
  reasoningEffort: AIReasoningEffort;
  temperature: AITemperature;
  maxOutputTokens: AIMaxOutputTokens;
  explanation: boolean;
}

export interface AISettings {
  white: AIPlayerSettings;
  black: AIPlayerSettings;
}

export const AI_MODELS: Record<AIProvider, AIModelOption[]> = {
  openai: [
    {
      id: "gpt-5.6-luna",
      name: "GPT-5.6 Luna — Cheapest",
      tier: "Cheapest",
    },
    {
      id: "gpt-5.6-terra",
      name: "GPT-5.6 Terra — Balanced",
      tier: "Balanced",
    },
    {
      id: "gpt-5.6-sol",
      name: "GPT-5.6 Sol — Best",
      tier: "Best",
    },
  ],
  anthropic: [
    {
      id: "claude-haiku-4-5-20251001",
      name: "Claude Haiku 4.5 — Cheapest — NOTIMPLEMENTED",
      tier: "Cheapest",
    },
    {
      id: "claude-sonnet-5",
      name: "Claude Sonnet 5 — Balanced — NOTIMPLEMENTED",
      tier: "Balanced",
    },
    {
      id: "claude-fable-5",
      name: "Claude Fable 5 — Best — NOTIMPLEMENTED",
      tier: "Best",
    },
  ],
};

export const DEFAULT_AI_PLAYER_SETTINGS: AIPlayerSettings = {
  provider: "openai",
  model: AI_MODELS.openai[0].id,
  reasoningEffort: "medium",
  temperature: 0.2,
  maxOutputTokens: 128,
  explanation: false,
};

export const DEFAULT_AI_SETTINGS: AISettings = {
  white: { ...DEFAULT_AI_PLAYER_SETTINGS },
  black: { ...DEFAULT_AI_PLAYER_SETTINGS },
};
