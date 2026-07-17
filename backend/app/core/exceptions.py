"""Custom exception hierarchy for clear, catchable error handling."""


class AssistantError(Exception):
    """Base class for all application-specific errors."""


class STTError(AssistantError):
    """Raised when speech-to-text transcription fails."""


class LLMError(AssistantError):
    """Raised when all configured LLM providers fail to respond."""


class TTSError(AssistantError):
    """Raised when speech synthesis fails on all configured providers."""


class VADError(AssistantError):
    """Raised when voice activity detection fails to process audio."""
