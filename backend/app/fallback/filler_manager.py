"""
Fallback Filler Manager.

Implements the "never leave the user waiting silently" requirement:
if a pipeline stage is taking longer than expected, the assistant plays
a short, natural filler phrase instead of a spinner or error message,
then continues once the real response is ready.
"""
import random

STT_FILLERS = [
    "I'm listening...",
    "Mm-hmm, go on...",
]

THINKING_FILLERS = [
    "Just a moment while I think...",
    "Interesting question, let me think about that...",
    "Let me work that out...",
    "Give me a second to think this through...",
]

RECOVERY_FILLERS = [
    "Sorry about that, let me try again.",
    "Let's give that another shot.",
]

APOLOGETIC_FALLBACK = (
    "I'm having a little trouble reaching my brain right now — "
    "could you say that again in a moment?"
)


def get_thinking_filler() -> str:
    """Return a random natural filler phrase to play while the LLM is slow."""
    return random.choice(THINKING_FILLERS)


def get_listening_filler() -> str:
    return random.choice(STT_FILLERS)


def get_recovery_filler() -> str:
    return random.choice(RECOVERY_FILLERS)


def get_apologetic_fallback() -> str:
    """Final, polite message when every provider has failed."""
    return APOLOGETIC_FALLBACK
