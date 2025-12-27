import { create } from "zustand";

export type PlayerMode = "human" | "engine";

interface GameState {
  fen: string;
  status: string;
  mode: PlayerMode;
  engine: string; // engine key, e.g., "random"
  setFen: (fen: string) => void;
  setStatus: (status: string) => void;
  setMode: (mode: PlayerMode) => void;
  setEngine: (engine: string) => void;
}

export const useGameStore = create<GameState>((set) => ({
  fen: "start",
  status: "ongoing",
  mode: "human",
  engine: "random",
  setFen: (fen) => set({ fen }),
  setStatus: (status) => set({ status }),
  setMode: (mode) => set({ mode }),
  setEngine: (engine) => set({ engine }),
}));
