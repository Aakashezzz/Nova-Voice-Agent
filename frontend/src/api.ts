import type { ConverseResponse, HealthResponse } from "./types";

const API_BASE = "/api";

/**
 * Sends a recorded utterance to the backend and returns the full pipeline
 * result (transcript, reply text, and a URL to fetch the reply audio).
 */
export async function converse(
  audioBlob: Blob,
  sessionId: string | null
): Promise<ConverseResponse> {
  const formData = new FormData();
  formData.append("audio", audioBlob, "utterance.webm");
  if (sessionId) {
    formData.append("session_id", sessionId);
  }

  const response = await fetch(`${API_BASE}/converse`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(body.detail || "The assistant could not process that.");
  }

  return response.json();
}

export async function clearSession(sessionId: string): Promise<void> {
  await fetch(`${API_BASE}/clear`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId }),
  });
}

export async function checkHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE}/health`);
  if (!response.ok) throw new Error("Health check failed");
  return response.json();
}

export function resolveAudioUrl(path: string): string {
  return path.startsWith("http") ? path : path;
}
