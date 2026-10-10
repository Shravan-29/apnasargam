import numpy as np

FRAME_SIZE = 2048
HOP_SIZE = 512
MIN_FREQ = 80.0    # roughly E2, lower bound for typical humming
MAX_FREQ = 1000.0  # roughly B5, upper bound
SILENCE_THRESHOLD = 0.01
MIN_NOTE_DURATION = 0.08  # ignore flickers shorter than ~80ms


def _autocorrelate_pitch(frame: np.ndarray, sample_rate: int) -> float | None:
    """
    Estimates the fundamental frequency of one audio frame via
    autocorrelation: the signal is correlated against shifted copies of
    itself, and the lag with the strongest correlation peak (within a
    plausible pitch range) corresponds to the period of the fundamental
    frequency. This is a classic, explainable pitch-detection method -
    simpler than FFT-based approaches and effective for monophonic
    humming, which has no competing harmonics from other instruments.
    """
    frame = frame - np.mean(frame)
    if np.max(np.abs(frame)) < SILENCE_THRESHOLD:
        return None

    corr = np.correlate(frame, frame, mode="full")
    corr = corr[len(corr) // 2:]

    min_lag = int(sample_rate / MAX_FREQ)
    max_lag = min(int(sample_rate / MIN_FREQ), len(corr) - 1)
    if min_lag >= max_lag:
        return None

    segment = corr[min_lag:max_lag]
    if len(segment) == 0 or np.max(segment) <= 0:
        return None

    peak_lag = min_lag + int(np.argmax(segment))
    if peak_lag == 0:
        return None

    return sample_rate / peak_lag


def _freq_to_midi(freq: float) -> int:
    return int(round(69 + 12 * np.log2(freq / 440.0)))


def detect_notes(samples: np.ndarray, sample_rate: int) -> list[tuple[int, float, float]]:
    """
    Runs frame-by-frame pitch detection across the recording, then
    collapses consecutive frames with a stable detected pitch into
    discrete note events. Returns (midi_pitch, start_seconds, duration_seconds).
    """
    num_frames = max(0, (len(samples) - FRAME_SIZE) // HOP_SIZE)
    frame_pitches: list[int | None] = []

    for i in range(num_frames):
        start = i * HOP_SIZE
        frame = samples[start:start + FRAME_SIZE]
        freq = _autocorrelate_pitch(frame, sample_rate)
        frame_pitches.append(_freq_to_midi(freq) if freq else None)

    notes = []
    current_pitch = None
    current_start_frame = None

    for i, pitch in enumerate(frame_pitches + [None]):  # sentinel flushes the last note
        if pitch != current_pitch:
            if current_pitch is not None and current_start_frame is not None:
                start_time = current_start_frame * HOP_SIZE / sample_rate
                end_time = i * HOP_SIZE / sample_rate
                if end_time - start_time > MIN_NOTE_DURATION:
                    notes.append((current_pitch, start_time, end_time - start_time))
            current_pitch = pitch
            current_start_frame = i

    return notes