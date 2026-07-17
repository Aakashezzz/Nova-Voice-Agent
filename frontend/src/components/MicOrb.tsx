import type { AssistantState } from "../types";

interface MicOrbProps {
  state: AssistantState;
  onToggle: () => void;
}

const STATE_LABEL: Record<AssistantState, string> = {
  idle: "Tap to speak",
  listening: "Listening...",
  processing: "Thinking...",
  speaking: "Speaking...",
  error: "Tap to try again",
};

const STATE_RING_COLOR: Record<AssistantState, string> = {
  idle: "border-line",
  listening: "border-signal",
  processing: "border-ember",
  speaking: "border-signal",
  error: "border-ember",
};

export function MicOrb({ state, onToggle }: MicOrbProps) {
  const isActive = state === "listening" || state === "speaking";

  return (
    <div className="flex flex-col items-center gap-4">
      <div className="relative flex h-40 w-40 items-center justify-center">
        {isActive && (
          <span className="absolute inset-0 rounded-full bg-signal/20 animate-pulseRing" />
        )}
        <button
          onClick={onToggle}
          disabled={state === "processing"}
          aria-label={STATE_LABEL[state]}
          className={`relative flex h-32 w-32 items-center justify-center rounded-full border-2 bg-panel
            transition-all duration-300 ease-out
            ${STATE_RING_COLOR[state]}
            ${state === "processing" ? "cursor-wait opacity-80" : "hover:scale-105 active:scale-95"}
          `}
        >
          {state === "processing" ? (
            <div className="flex items-end gap-1 h-8">
              {[0, 1, 2, 3].map((i) => (
                <span
                  key={i}
                  className="w-1.5 rounded-full bg-ember animate-wave"
                  style={{ height: "100%", animationDelay: `${i * 0.12}s` }}
                />
              ))}
            </div>
          ) : (
            <svg
              width="36"
              height="36"
              viewBox="0 0 24 24"
              fill="none"
              stroke={isActive ? "#5EE6C7" : "#8992A6"}
              strokeWidth="1.75"
            >
              <rect x="9" y="2" width="6" height="12" rx="3" />
              <path d="M5 10a7 7 0 0 0 14 0" />
              <line x1="12" y1="19" x2="12" y2="22" />
            </svg>
          )}
        </button>
      </div>
      <p className="font-mono text-sm tracking-wide text-mist">{STATE_LABEL[state]}</p>
    </div>
  );
}
