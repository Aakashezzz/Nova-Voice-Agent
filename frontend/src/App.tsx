import { MicOrb } from "./components/MicOrb";
import { StatusBar } from "./components/StatusBar";
import { TranscriptPanel } from "./components/TranscriptPanel";
import { useVoiceAssistant } from "./hooks/useVoiceAssistant";

export default function App() {
  const {
    state,
    transcript,
    thinkingPhrase,
    latency,
    modelUsed,
    errorMessage,
    toggleMic,
    clearConversation,
  } = useVoiceAssistant();

  return (
    <div className="flex h-screen flex-col bg-ink text-gray-100">
      <StatusBar modelUsed={modelUsed} latency={latency} onClear={clearConversation} />

      <header className="px-6 pt-8 pb-2">
        <h1 className="font-display text-2xl font-bold tracking-tight">
          Voice<span className="text-signal">Assistant</span>
        </h1>
        <p className="mt-1 text-sm text-mist">
          A real-time, audio-in audio-out conversational AI.
        </p>
      </header>

      <main className="flex flex-1 flex-col gap-6 overflow-hidden px-6 pb-6 md:flex-row">
        <section className="flex flex-1 flex-col rounded-2xl border border-line bg-panel/40 p-4">
          <TranscriptPanel entries={transcript} thinkingPhrase={thinkingPhrase} />
        </section>

        <section className="flex w-full flex-col items-center justify-center gap-6 rounded-2xl border border-line bg-panel/40 p-8 md:w-80">
          <MicOrb state={state} onToggle={toggleMic} />
          {errorMessage && (
            <p className="max-w-xs text-center font-mono text-xs text-ember">{errorMessage}</p>
          )}
        </section>
      </main>
    </div>
  );
}
