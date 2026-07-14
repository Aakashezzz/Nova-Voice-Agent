from app.audio.recorder import AudioRecorder


def main():

    recorder = AudioRecorder()

    recorder.record(
        duration=5,
        filename="audio.wav",
    )


if __name__ == "__main__":
    main()