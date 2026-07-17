export type AssistantState =
  | "idle"
  | "listening"
  | "processing"
  | "speaking"
  | "error";

export interface ConverseResponse {
  session_id: string;
  transcript: string;
  reply_text: string;
  llm_provider_used: string;
  tts_provider_used: string;
  audio_url: string;
  latency_ms: Record<string, number>;
  used_fallback_filler: boolean;
}

export interface TranscriptEntry {
  id: string;
  role: "user" | "assistant";
  text: string;
  timestamp: number;
}

export interface HealthResponse {
  status: string;
  app_name: string;
  stt_ready: boolean;
  llm_provider: string;
  tts_provider: string;
}
