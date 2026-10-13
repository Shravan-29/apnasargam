import io
import wave

import numpy as np
import pytest

from app.generation.audio_utils import read_wav_as_samples
from app.generation.pitch_detection import detect_notes

SR = 44100


def tone(freq, seconds, sr=SR, amp=0.5):
    t = np.arange(int(seconds * sr)) / sr
    return (amp * np.sin(2 * np.pi * freq * t)).astype(np.float32)


def voice(freq, seconds, sr=SR, amp=0.4):
    """Harmonic-rich note with soft attack/release, closer to a hum than a sine."""
    t = np.arange(int(seconds * sr)) / sr
    sig = sum(h * np.sin(2 * np.pi * freq * (i + 1) * t) for i, h in enumerate((1.0, 0.6, 0.4, 0.25)))
    env = np.minimum(1, np.minimum(t / 0.03, (seconds - t) / 0.03))
    return (amp * sig / np.max(np.abs(sig)) * env).astype(np.float32)


def silence(seconds, sr=SR):
    return np.zeros(int(seconds * sr), dtype=np.float32)


def to_wav_bytes(samples, sr=SR, channels=1, width=2):
    """Encode the same way the browser recorder does: 16-bit PCM WAV."""
    if width == 2:
        pcm = (np.clip(samples, -1, 1) * 32767).astype("<i2").tobytes()
    else:
        pcm = ((np.clip(samples, -1, 1) * 127) + 128).astype("u1").tobytes()
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(channels)
        w.setsampwidth(width)
        w.setframerate(sr)
        w.writeframes(pcm)
    return buf.getvalue()


@pytest.mark.parametrize("sample_rate", [16000, 44100, 48000])
@pytest.mark.parametrize("freq,expected_midi", [(196.0, 55), (220.0, 57), (329.63, 64), (440.0, 69), (523.25, 72)])
def test_pure_tone_maps_to_the_correct_midi_note(freq, expected_midi, sample_rate):
    notes = detect_notes(tone(freq, 1.0, sample_rate), sample_rate)
    assert [p for p, _, _ in notes] == [expected_midi]


def test_melody_with_gaps_is_recovered_note_by_note():
    freqs = {"C4": 261.63, "E4": 329.63, "G4": 392.00}
    audio = np.concatenate(
        [np.concatenate([voice(freqs[n], 0.5), silence(0.15)]) for n in ("C4", "E4", "G4", "E4", "C4")]
    )
    notes = detect_notes(audio, SR)

    assert [p for p, _, _ in notes] == [60, 64, 67, 64, 60]
    expected_onsets = [0.0, 0.65, 1.30, 1.95, 2.60]
    for (_, start, _), expected in zip(notes, expected_onsets):
        assert abs(start - expected) < 0.1


def test_background_noise_does_not_change_the_detected_notes():
    rng = np.random.default_rng(0)
    freqs = [261.63, 329.63, 392.00]
    audio = np.concatenate([np.concatenate([voice(f, 0.5), silence(0.15)]) for f in freqs])
    noisy = audio + rng.normal(0, 0.02, size=audio.shape).astype(np.float32)

    assert [p for p, _, _ in detect_notes(noisy, SR)] == [60, 64, 67]


def test_vibrato_stays_a_single_note():
    t = np.arange(SR) / SR
    freq = 261.63 * 2 ** ((20 * np.sin(2 * np.pi * 5 * t)) / 1200)  # +-20 cents at 5 Hz
    phase = 2 * np.pi * np.cumsum(freq) / SR
    audio = (0.4 * (np.sin(phase) + 0.6 * np.sin(2 * phase))).astype(np.float32)

    assert [p for p, _, _ in detect_notes(audio, SR)] == [60]


def test_same_note_with_a_gap_is_two_notes():
    audio = np.concatenate([voice(261.63, 1.0), silence(0.1), voice(261.63, 1.0)])
    assert [p for p, _, _ in detect_notes(audio, SR)] == [60, 60]


def test_known_limitation_same_note_without_a_gap_merges_into_one():
    """
    Documents a real limitation rather than hiding it: onsets are found by
    pitch change or silence only, so repeating a note with no dip in between
    is detected as one long note. If onset detection is ever added, this
    test should be updated to expect two notes.
    """
    audio = np.concatenate([voice(261.63, 1.0), voice(261.63, 1.0)])
    notes = detect_notes(audio, SR)
    assert len(notes) == 1
    assert notes[0][2] > 1.5


@pytest.mark.parametrize(
    "samples",
    [silence(2.0), tone(440.0, 0.01), np.zeros(0, dtype=np.float32)],
    ids=["silence", "shorter-than-one-frame", "empty"],
)
def test_nothing_to_detect_returns_an_empty_list(samples):
    assert detect_notes(samples, SR) == []


def test_wav_roundtrip_keeps_the_pitch():
    samples, rate = read_wav_as_samples(to_wav_bytes(tone(440.0, 1.0)))
    assert rate == SR
    assert [p for p, _, _ in detect_notes(samples, rate)] == [69]


def test_stereo_wav_is_downmixed_to_mono():
    mono = tone(440.0, 0.5)
    stereo = np.repeat(mono, 2)  # interleaved L/R
    samples, _ = read_wav_as_samples(to_wav_bytes(stereo, channels=2))
    assert samples.shape[0] == mono.shape[0]


def test_non_16_bit_wav_is_rejected_with_a_clear_error():
    with pytest.raises(ValueError):
        read_wav_as_samples(to_wav_bytes(tone(440.0, 0.2), width=1))