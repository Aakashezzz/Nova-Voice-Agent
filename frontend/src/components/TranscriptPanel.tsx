import { useEffect, useRef } from "react";
import type { TranscriptEntry } from "../types";

interface TranscriptPanelProps {
  entries: TranscriptEntry[];
  thinkingPhrase: string | null;
}

export function TranscriptPanel({ entries, thinkingPhrase }: TranscriptPanelProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [entries, thinkingPhrase]);

  if (entries.length === 0 && !thinkingPhrase) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-2 text-mist">
        <p className="font-display text-lg">Your conversation will appear here</p>
        <p className="font-mono text-xs">Tap the mic and start talking</p>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col gap-3 overflow-y-auto px-1 py-2">
      {entries.map((entry) => (
        <div
          key={entry.id}
          className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
            entry.role === "user"
              ? "self-end bg-signal/10 text-signal border border-signal/30"
              : "self-start bg-panel text-gray-100 border border-line"
          }`}
        >
          <span className="mb-1 block font-mono text-[10px] uppercase tracking-widest text-mist">
            {entry.role === "user" ? "You" : "Assistant"}
          </span>
          {entry.text}
        </div>
      ))}

      {thinkingPhrase && (
        <div className="self-start max-w-[80%] rounded-2xl border border-line bg-panel px-4 py-3 text-sm italic text-mist">
          {thinkingPhrase}
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
