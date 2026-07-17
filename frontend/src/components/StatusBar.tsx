import { useEffect, useState } from "react";
import { checkHealth } from "../api";

interface StatusBarProps {
  modelUsed: string | null;
  latency: Record<string, number> | null;
  onClear: () => void;
}

export function StatusBar({ modelUsed, latency, onClear }: StatusBarProps) {
  const [connected, setConnected] = useState<boolean | null>(null);

  useEffect(() => {
    let mounted = true;
    const poll = async () => {
      try {
        await checkHealth();
        if (mounted) setConnected(true);
      } catch {
        if (mounted) setConnected(false);
      }
    };
    poll();
    const interval = window.setInterval(poll, 15_000);
    return () => {
      mounted = false;
      window.clearInterval(interval);
    };
  }, []);

  const totalMs = latency?.total_ms;

  return (
    <div className="flex w-full items-center justify-between border-b border-line px-6 py-4 font-mono text-xs text-mist">
      <div className="flex items-center gap-2">
        <span
          className={`h-2 w-2 rounded-full ${
            connected === null ? "bg-mist" : connected ? "bg-signal" : "bg-ember"
          }`}
        />
        <span>
          {connected === null ? "Checking..." : connected ? "Connected" : "Offline"}
        </span>
      </div>

      <div className="flex items-center gap-6">
        {modelUsed && (
          <span>
            Model: <span className="text-gray-200">{modelUsed}</span>
          </span>
        )}
        {totalMs !== undefined && (
          <span>
            Latency:{" "}
            <span className={totalMs < 2000 ? "text-signal" : "text-ember"}>
              {Math.round(totalMs)}ms
            </span>
          </span>
        )}
        <button
          onClick={onClear}
          className="rounded-md border border-line px-3 py-1.5 text-mist transition-colors hover:border-ember hover:text-ember"
        >
          Clear conversation
        </button>
      </div>
    </div>
  );
}
