import { useCallback, useEffect, useRef, useState } from "react";
import { clearSession, converse } from "../api";
import type { AssistantState, TranscriptEntry } from "../types";
import { useAudioRecorder } from "./useAudioRecorder";

const THINKING_FILLER_DELAY_MS = 1200;
const THINKING_PHRASES = [
  "Just a moment while I think...",
  "Interesting question, let me think about that...",
  "Let me work that out...",
];

let uid = 0;
const nextId = () => `${Date.now()}-${uid++}`;

export function useVoiceAssistant() {
  const [state, setState] = useState<AssistantState>("idle");
  const [transcript, setTranscript] = useState<TranscriptEntry[]>([]);
  const [thinkingPhrase, setThinkingPhrase] = useState<string | null>(null);
  const [latency, setLatency] = useState<Record<string, number> | null>(null);
  const [modelUsed, setModelUsed] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const sessionIdRef = useRef<string | null>(null);
  const fillerTimerRef = useRef<number | null>(null);
  const audioPlayerRef = useRef<HTMLAudioElement | null>(null);

  const handleRecordingStop = useCallback(async (blob: Blob) => {
    setState("processing");

    fillerTimerRef.current = window.setTimeout(() => {
      setThinkingPhrase(THINKING_PHRASES[Math.floor(Math.random() * THINKING_PHRASES.length)]);
    }, THINKING_FILLER_DELAY_MS);

    try {
      const result = await converse(blob, sessionIdRef.current);
      sessionIdRef.current = result.session_id;
      setLatency(result.latency_ms);
      setModelUsed(result.llm_provider_used);

      setTranscript((prev) => [
        ...prev,
        { id: nextId(), role: "user", text: result.transcript, timestamp: Date.now() },
        { id: nextId(), role: "assistant", text: result.reply_text, timestamp: Date.now() },
      ]);

      if (fillerTimerRef.current) window.clearTimeout(fillerTimerRef.current);
      setThinkingPhrase(null);
      setState("speaking");

      const audio = new Audio(result.audio_url);
      audioPlayerRef.current = audio;
      audio.onended = () => setState("idle");
      audio.onerror = () => setState("idle");
      await audio.play();
    } catch (err) {
      if (fillerTimerRef.current) window.clearTimeout(fillerTimerRef.current);
      setThinkingPhrase(null);
      setErrorMessage(err instanceof Error ? err.message : "Something went wrong.");
      setState("error");
    }
  }, []);

  const handleNoSpeechDetected = useCallback(() => {
  setState("idle");
  setErrorMessage("I didn't catch that — tap the mic and try again.");
  }, []);

const recorder = useAudioRecorder({
  onStop: handleRecordingStop,
  onNoSpeechDetected: handleNoSpeechDetected,
});

  const startListening = useCallback(async () => {
    setErrorMessage(null);
    setState("listening");
    try {
      await recorder.start();
    } catch (err) {
      setErrorMessage("Microphone access was denied or unavailable.");
      setState("error");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const stopListening = useCallback(() => {
    recorder.stop();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const toggleMic = useCallback(() => {
    if (state === "listening") {
      stopListening();
    } else if (state === "idle" || state === "error") {
      startListening();
    }
  }, [state, startListening, stopListening]);

  const clearConversation = useCallback(async () => {
    if (sessionIdRef.current) {
      await clearSession(sessionIdRef.current).catch(() => undefined);
    }
    setTranscript([]);
    setLatency(null);
    setModelUsed(null);
    setState("idle");
  }, []);

  useEffect(() => {
    return () => {
      if (fillerTimerRef.current) window.clearTimeout(fillerTimerRef.current);
      audioPlayerRef.current?.pause();
    };
  }, []);

  return {
    state,
    transcript,
    thinkingPhrase,
    latency,
    modelUsed,
    errorMessage,
    toggleMic,
    clearConversation,
  };
}
