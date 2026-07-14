from dataclasses import dataclass


@dataclass
class AudioDevice:
    """
    Represents a microphone/input audio device.
    """

    id: int
    name: str
    channels: int