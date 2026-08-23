import React from "react";
import {
  AI_MODELS,
  type AIColor,
  type AIMaxOutputTokens,
  type AIPlayerSettings,
  type AIProvider,
  type AIReasoningEffort,
  type AISettings,
  type AITemperature,
} from "../api/aiSettings";
import "../styles/ControlPanel.css";

interface ControlPanelProps {
  onReset?: () => void;
  onFlip?: () => void;
  onEngineSettings?: () => void;
  onAISettings?: () => void;

  whiteDepth: number;
  blackDepth: number;
  setWhiteDepth: (v: number) => void;
  setBlackDepth: (v: number) => void;

  aiSettings: AISettings;
  setAISettings: React.Dispatch<React.SetStateAction<AISettings>>;

  showEngineSettings: boolean;
  showAISettings: boolean;
}

interface AIPlayerSettingsPanelProps {
  color: AIColor;
  settings: AIPlayerSettings;
  onSettingChange: <K extends keyof AIPlayerSettings>(
    key: K,
    value: AIPlayerSettings[K],
  ) => void;
  onProviderChange: (provider: AIProvider) => void;
}

const REASONING_OPTIONS: Array<{
  value: AIReasoningEffort;
  label: string;
}> = [
  { value: "low", label: "Low" },
  { value: "medium", label: "Med" },
  { value: "high", label: "High" },
];

const AIPlayerSettingsPanel: React.FC<AIPlayerSettingsPanelProps> = ({
  color,
  settings,
  onSettingChange,
  onProviderChange,
}) => {
  const label = color === "white" ? "White" : "Black";
  const idPrefix = `ai-${color}`;
  const availableModels = AI_MODELS[settings.provider];

  return (
    <div className="ai-player-settings">
      <div className="ai-player-settings-title">{label} AI</div>

      <div className="engine-setting-row">
        <label htmlFor={`${idPrefix}-provider`}>Provider</label>
        <select
          id={`${idPrefix}-provider`}
          value={settings.provider}
          onChange={(e) => onProviderChange(e.target.value as AIProvider)}
        >
          <option value="openai">OpenAI — NOTIMPLEMENTED</option>
          <option value="anthropic">Anthropic — NOTIMPLEMENTED</option>
        </select>
      </div>

      <div className="engine-setting-row">
        <label htmlFor={`${idPrefix}-model`}>Model</label>
        <select
          id={`${idPrefix}-model`}
          value={settings.model}
          onChange={(e) => onSettingChange("model", e.target.value)}
        >
          {availableModels.map((model) => (
            <option key={model.id} value={model.id}>
              {model.name}
            </option>
          ))}
        </select>
      </div>

      <div className="engine-setting-row">
        <label>Reasoning</label>
        <div className="ai-checkbox-group">
          {REASONING_OPTIONS.map((option) => (
            <label
              key={option.value}
              className="ai-checkbox-option"
              htmlFor={`${idPrefix}-reasoning-${option.value}`}
            >
              <input
                id={`${idPrefix}-reasoning-${option.value}`}
                type="checkbox"
                checked={settings.reasoningEffort === option.value}
                onChange={() =>
                  onSettingChange("reasoningEffort", option.value)
                }
              />
              <span>{option.label}</span>
            </label>
          ))}
        </div>
      </div>

      <div className="ai-dual-setting-row">
        <div className="ai-compact-select">
          <label htmlFor={`${idPrefix}-temperature`}>Temperature</label>
          <select
            id={`${idPrefix}-temperature`}
            value={settings.temperature}
            onChange={(e) =>
              onSettingChange(
                "temperature",
                Number(e.target.value) as AITemperature,
              )
            }
          >
            <option value={0}>0.0</option>
            <option value={0.2}>0.2</option>
            <option value={0.5}>0.5</option>
            <option value={0.8}>0.8</option>
            <option value={1}>1.0</option>
          </select>
        </div>

        <div className="ai-compact-select">
          <label htmlFor={`${idPrefix}-max-output`}>Max tokens</label>
          <select
            id={`${idPrefix}-max-output`}
            value={settings.maxOutputTokens}
            onChange={(e) =>
              onSettingChange(
                "maxOutputTokens",
                Number(e.target.value) as AIMaxOutputTokens,
              )
            }
          >
            <option value={32}>32</option>
            <option value={64}>64</option>
            <option value={128}>128</option>
            <option value={256}>256</option>
          </select>
        </div>
      </div>

      <div className="ai-inline-setting-row">
        <span className="ai-inline-setting-label">Response</span>
        <label
          className="ai-checkbox-option"
          htmlFor={`${idPrefix}-explanation`}
        >
          <input
            id={`${idPrefix}-explanation`}
            type="checkbox"
            checked={settings.explanation}
            onChange={(e) => onSettingChange("explanation", e.target.checked)}
          />
          <span>Explanation</span>
        </label>
      </div>
    </div>
  );
};

export const ControlPanel: React.FC<ControlPanelProps> = ({
  onReset,
  onFlip,
  onEngineSettings,
  onAISettings,
  whiteDepth,
  blackDepth,
  setWhiteDepth,
  setBlackDepth,
  aiSettings,
  setAISettings,
  showEngineSettings,
  showAISettings,
}) => {
  const updateAISetting = <K extends keyof AIPlayerSettings>(
    color: AIColor,
    key: K,
    value: AIPlayerSettings[K],
  ) => {
    setAISettings((current) => ({
      ...current,
      [color]: {
        ...current[color],
        [key]: value,
      },
    }));
  };

  const handleProviderChange = (color: AIColor, provider: AIProvider) => {
    setAISettings((current) => ({
      ...current,
      [color]: {
        ...current[color],
        provider,
        model: AI_MODELS[provider][0].id,
      },
    }));
  };

  return (
    <div className="control-panel">
      <button className="control-panel-button" onClick={onReset}>
        🔄 Reset
      </button>

      <button className="control-panel-button" onClick={onFlip}>
        🔃 Flip
      </button>

      <button className="control-panel-button" onClick={onEngineSettings}>
        ⚙️ Engine
      </button>

      <button className="control-panel-button" onClick={onAISettings}>
        🧠 AI
      </button>

      <div
        className={`engine-settings-panel ${showEngineSettings ? "open" : ""}`}
      >
        <div className="engine-settings-title">Engine Settings</div>

        <div className="engine-slider">
          <label>White depth: {whiteDepth}</label>
          <input
            type="range"
            min="1"
            max="15"
            value={whiteDepth}
            onChange={(e) => setWhiteDepth(Number(e.target.value))}
          />
        </div>

        <div className="engine-slider">
          <label>Black depth: {blackDepth}</label>
          <input
            type="range"
            min="1"
            max="15"
            value={blackDepth}
            onChange={(e) => setBlackDepth(Number(e.target.value))}
          />
        </div>
      </div>

      <div
        className={`engine-settings-panel ai-settings-panel ${showAISettings ? "open" : ""}`}
      >
        <div className="engine-settings-title">AI Settings</div>

        <div className="ai-player-settings-grid">
          <AIPlayerSettingsPanel
            color="white"
            settings={aiSettings.white}
            onSettingChange={(key, value) =>
              updateAISetting("white", key, value)
            }
            onProviderChange={(provider) =>
              handleProviderChange("white", provider)
            }
          />

          <AIPlayerSettingsPanel
            color="black"
            settings={aiSettings.black}
            onSettingChange={(key, value) =>
              updateAISetting("black", key, value)
            }
            onProviderChange={(provider) =>
              handleProviderChange("black", provider)
            }
          />
        </div>
      </div>
    </div>
  );
};
