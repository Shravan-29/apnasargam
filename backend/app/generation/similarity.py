import os
import numpy as np
import pretty_midi

MIDI_DIR = "generated_midi"

# How large a gap on each feature counts as "clearly different":
# average pitch 6 semitones, pitch range 10 semitones, note density
# 1 note per beat, tempo 25 BPM. Features are divided by these before
# comparison, so no single feature (BPM, which is numerically huge)
# dominates just because of its units.
FEATURE_SCALE = np.array([6.0, 10.0, 1.0, 25.0])


def extract_feature_vector(midi_filename: str, bpm: int) -> np.ndarray:
    """
    Extracts four interpretable features from a generated track:
    [average pitch, pitch range, note density (notes per beat), tempo].
    Drum tracks are ignored. Deliberately simple and explainable rather
    than a learned embedding.
    """
    path = os.path.join(MIDI_DIR, midi_filename)
    midi = pretty_midi.PrettyMIDI(path)

    pitches = []
    for instrument in midi.instruments:
        if instrument.is_drum:
            continue
        for note in instrument.notes:
            pitches.append(note.pitch)

    if not pitches:
        return np.zeros(4)

    duration_beats = max(midi.get_end_time() * bpm / 60.0, 1.0)

    return np.array([
        float(np.mean(pitches)),
        float(max(pitches) - min(pitches)),
        len(pitches) / duration_beats,
        float(bpm),
    ])


def similarity_score(a: np.ndarray, b: np.ndarray) -> float:
    """
    Gaussian (RBF) similarity over the scaled feature vectors, in [0, 1]:
    1.0 for identical tracks, falling smoothly toward 0 as they differ.

    This replaced a first version that used cosine similarity on the raw
    features. Measured on six synthetic tracks, that version scored
    every pair between 98.5% and 99.97%, because the vectors are all
    positive and dominated by BPM and pitch magnitude, so it could not
    tell a calm track from an energetic one. Centering the features
    first fixed the ranking but made typical tracks (near the center)
    match nothing, since cosine is undefined near the origin. A distance
    based score has neither problem.
    """
    distance = np.linalg.norm((a - b) / FEATURE_SCALE)
    return float(np.exp(-0.5 * distance * distance))