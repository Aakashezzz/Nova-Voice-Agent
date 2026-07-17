import { useCallback, useRef, useState } from "react";

interface UseAudioRecorderOptions {
  /** How long (ms) of near-silence ends the recording automatically, once speech has started. */
  silenceTimeoutMs?: number;
  /** Volume (0-255) below which audio is considered silence. */
  silenceThreshold?: number;
  /** Max time (ms) to wait for the user to start speaking before giving up. */
  maxWaitForSpeechMs?: number;
  onStop?: (blob: Blob) => void;
  /** Called if no speech was detected at all within maxWaitForSpeechMs. */
  onNoSpeechDetected?: () => void;
}

/**
 * Records microphone audio and automatically stops shortly after the user
 * goes quiet, approximating server-side VAD behaviour on the client so the
 * user doesn't have to manually stop each turn.
 *
 * Important: the silence-based auto-stop timer only arms *after* speech has
 * actually been detected at least once. Without this, a natural pause
 * between clicking the mic and starting to talk would itself look like
 * "silence" and cut the recording off before any speech was captured.
 */
export function useAudioRecorder({
  silenceTimeoutMs = 1200,
  silenceThreshold = 8,
  maxWaitForSpeechMs = 8000,
  onStop,
  onNoSpeechDetected,
}: UseAudioRecorderOptions = {}) {
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const silenceTimerRef = useRef<number | null>(null);
  const noSpeechTimerRef = useRef<number | null>(null);
  const hasDetectedSpeechRef = useRef(false);
  const gaveUpWaitingRef = useRef(false);
  const chunksRef = useRef<Blob[]>([]);

  const cleanup = useCallback(() => {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    audioContextRef.current?.close().catch(() => undefined);
    if (silenceTimerRef.current) window.clearTimeout(silenceTimerRef.current);
    if (noSpeechTimerRef.current) window.clearTimeout(noSpeechTimerRef.current);
    streamRef.current = null;
    audioContextRef.current = null;
    silenceTimerRef.current = null;
    noSpeechTimerRef.current = null;
  }, []);

  const monitorSilence = useCallback(
    (stream: MediaStream, onSilenceDetected: () => void, onGaveUpWaiting: () => void) => {
      const audioContext = new AudioContext();
      audioContextRef.current = audioContext;
      const source = audioContext.createMediaStreamSource(stream);
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 512;
      source.connect(analyser);

      const data = new Uint8Array(analyser.frequencyBinCount);
      hasDetectedSpeechRef.current = false;

      // If the user never starts speaking at all, stop waiting eventually
      // instead of recording indefinitely.
      noSpeechTimerRef.current = window.setTimeout(() => {
        if (!hasDetectedSpeechRef.current) onGaveUpWaiting();
      }, maxWaitForSpeechMs);

      const tick = () => {
        if (!audioContextRef.current) return; // stopped
        analyser.getByteFrequencyData(data);
        const volume = data.reduce((sum, v) => sum + v, 0) / data.length;
        const isSpeaking = volume >= silenceThreshold;

        if (isSpeaking && !hasDetectedSpeechRef.current) {
          // First time we've heard actual speech: cancel the "gave up
          // waiting" timer and start allowing silence to end the turn.
          hasDetectedSpeechRef.current = true;
          if (noSpeechTimerRef.current) {
            window.clearTimeout(noSpeechTimerRef.current);
            noSpeechTimerRef.current = null;
          }
        }

        if (hasDetectedSpeechRef.current) {
          if (isSpeaking) {
            if (silenceTimerRef.current !== null) {
              window.clearTimeout(silenceTimerRef.current);
              silenceTimerRef.current = null;
            }
          } else if (silenceTimerRef.current === null) {
            silenceTimerRef.current = window.setTimeout(() => {
              onSilenceDetected();
            }, silenceTimeoutMs);
          }
        }

        requestAnimationFrame(tick);
      };
      tick();
    },
    [silenceThreshold, silenceTimeoutMs, maxWaitForSpeechMs]
  );

  const start = useCallback(async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    streamRef.current = stream;
    chunksRef.current = [];

    const recorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
    mediaRecorderRef.current = recorder;

    recorder.ondataavailable = (event) => {
      if (event.data.size > 0) chunksRef.current.push(event.data);
    };

    recorder.onstop = () => {
      const blob = new Blob(chunksRef.current, { type: "audio/webm" });
      const gaveUp = gaveUpWaitingRef.current;
      cleanup();
      setIsRecording(false);
      if (gaveUp) {
        onNoSpeechDetected?.();
      } else {
        onStop?.(blob);
      }
    };

    gaveUpWaitingRef.current = false;
    recorder.start();
    setIsRecording(true);

    monitorSilence(
      stream,
      () => {
        // Normal case: user spoke, then went quiet — end the turn.
        if (mediaRecorderRef.current?.state === "recording") {
          mediaRecorderRef.current.stop();
        }
      },
      () => {
        // Edge case: mic was on but the user never said anything at all.
        // Stop cleanly without sending an (empty) clip to the backend.
        gaveUpWaitingRef.current = true;
        if (mediaRecorderRef.current?.state === "recording") {
          mediaRecorderRef.current.stop();
        }
      }
    );
  }, [cleanup, monitorSilence, onStop, onNoSpeechDetected]);

  const stop = useCallback(() => {
    if (mediaRecorderRef.current?.state === "recording") {
      mediaRecorderRef.current.stop();
    }
  }, []);

  return { isRecording, start, stop };
}