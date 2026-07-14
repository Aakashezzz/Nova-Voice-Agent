import numpy as np
import sounddevice as sd
import soundfile as sf

from app.audio.constants import (
    SAMPLE_RATE,
    CHANNELS,
    DTYPE,
)


class AudioRecorder:

    def record(self, duration: int, filename: str):

        print(f"\nRecording for {duration} seconds...")

        recording = sd.rec(
            int(duration * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype=DTYPE,
        )

        sd.wait()

        sf.write(
            filename,
            recording,
            SAMPLE_RATE,
        )

        print(f"\nSaved to {filename}")