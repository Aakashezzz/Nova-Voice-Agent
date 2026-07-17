"""
Audio conversion helpers.

The browser sends audio as WebM/Opus (via MediaRecorder) or raw PCM
depending on the frontend implementation. These helpers normalise
incoming audio bytes into the 16kHz mono float32 numpy array that both
Silero VAD and Faster-Whisper expect.
"""
import io
import logging

import numpy as np
from pydub import AudioSegment, silence
import soundfile as sf

logger = logging.getLogger(__name__)

TARGET_SAMPLE_RATE = 16_000

# If the loudest sample in the decoded clip is below this, the audio is
# almost certainly silence/near-silence (wrong input device, muted mic,
# mic gain too low) rather than quiet-but-real speech.
QUIET_AUDIO_WARNING_THRESHOLD = 0.02

# Cap how much gain we'll apply when boosting a quiet clip. Without a cap,
# a near-silent recording (mostly room noise) gets amplified so hard that
# the noise floor itself becomes loud enough for Whisper to hallucinate
# words from it. 15dB is enough to rescue genuinely-quiet speech without
# turning silence into garbage.
MAX_GAIN_DB = 15.0
TARGET_DBFS = -3.0


def decode_audio_bytes(raw_bytes: bytes, content_type: str = "audio/webm") -> np.ndarray:
    """
    Decode arbitrary uploaded audio bytes into a mono float32 numpy array
    resampled to 16kHz, as required by Whisper and Silero VAD.

    Leading/trailing silence is trimmed first, then the clip is gently
    gain-boosted (capped at MAX_GAIN_DB) if it's quiet. The cap matters:
    unbounded normalization on a mostly-silent recording amplifies room
    noise into something loud enough for Whisper to "hear" words in it.
    """
    try:
        # pydub (via ffmpeg) handles webm/ogg/mp3/wav transparently.
        audio_segment = AudioSegment.from_file(io.BytesIO(raw_bytes))
        audio_segment = audio_segment.set_frame_rate(TARGET_SAMPLE_RATE).set_channels(1)

        # Trim leading/trailing silence so we're not normalizing against
        # long stretches of pure noise (which would skew the gain calc).
        nonsilent_ranges = silence.detect_nonsilent(
            audio_segment, min_silence_len=200, silence_thresh=audio_segment.dBFS - 20
        )
        if nonsilent_ranges:
            start_ms = max(0, nonsilent_ranges[0][0] - 350)
            end_ms = min(len(audio_segment), nonsilent_ranges[-1][1] + 350)
            audio_segment = audio_segment[start_ms:end_ms]

        # Gentle, capped gain boost instead of full peak normalization.
        if audio_segment.dBFS != float("-inf"):
            gain_needed = TARGET_DBFS - audio_segment.dBFS
            gain_to_apply = max(0.0, min(gain_needed, MAX_GAIN_DB))
            if gain_to_apply > 0:
                audio_segment = audio_segment.apply_gain(gain_to_apply)

        samples = np.array(audio_segment.get_array_of_samples()).astype(np.float32)
        if samples.size == 0:
            logger.warning("Audio contained no non-silent segments after trimming.")
            return samples

        # Normalise int16 PCM range to [-1.0, 1.0]
        samples /= np.iinfo(np.int16).max

        peak = float(np.max(np.abs(samples)))
        duration_s = samples.size / TARGET_SAMPLE_RATE
        logger.info("Decoded audio: %.2fs, peak amplitude=%.4f", duration_s, peak)

        if peak < QUIET_AUDIO_WARNING_THRESHOLD:
            logger.warning(
                "Decoded audio is very quiet (peak=%.4f) even after gain boost. "
                "This usually means the wrong input device is selected, the mic "
                "is muted, or mic gain is too low at the OS level.",
                peak,
            )

        return samples
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to decode audio: %s", exc)
        raise ValueError(f"Unsupported or corrupt audio data: {exc}") from exc


def float_pcm_to_wav_bytes(samples: np.ndarray, sample_rate: int = TARGET_SAMPLE_RATE) -> bytes:
    """Encode a float32 mono PCM array back to WAV bytes for HTTP responses."""
    buffer = io.BytesIO()
    sf.write(buffer, samples, sample_rate, format="WAV", subtype="PCM_16")
    return buffer.getvalue()