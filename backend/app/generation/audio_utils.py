import io
import wave
import numpy as np


def read_wav_as_samples(file_bytes: bytes) -> tuple[np.ndarray, int]:
    """
    Reads a 16-bit PCM WAV file (encoded client-side in the browser,
    specifically to avoid needing ffmpeg on the backend to decode
    WebM/Opus recordings) into a normalized float32 mono sample array.
    """
    with wave.open(io.BytesIO(file_bytes), "rb") as wf:
        sample_rate = wf.getframerate()
        n_frames = wf.getnframes()
        raw = wf.readframes(n_frames)
        sample_width = wf.getsampwidth()
        channels = wf.getnchannels()

    if sample_width != 2:
        raise ValueError("Expected 16-bit PCM WAV audio")

    samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    if channels > 1:
        samples = samples.reshape(-1, channels).mean(axis=1)

    return samples, sample_rate