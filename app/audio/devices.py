import sounddevice as sd
from app.audio.models import AudioDevice


def list_input_devices() -> list[AudioDevice]:
    """
    Returns a list of all available microphone devices.
    """

    devices = sd.query_devices()
    microphones = []

    for index, device in enumerate(devices):
        if device["max_input_channels"] > 0:
            microphones.append(
                AudioDevice(
                    id=index,
                    name=device["name"],
                    channels=device["max_input_channels"],
                )
            )

    return microphones