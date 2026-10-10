import os
import numpy as np
import pretty_midi

MIDI_DIR = "generated_midi"


def extract_feature_vector(midi_filename: str, bpm: int) -> np.ndarray:
    """
    Extracts a small, interpretable feature vector from a generated
    track: average pitch, pitch range, note density (notes per beat),
    and tempo. Deliberately simple and explainable rather than a
    learned embedding - the goal is a transparent "tracks like this
    one" signal, not state-of-the-art music retrieval.
    """
    path = os.path.join(MIDI_DIR, midi_filename)
    midi = pretty_midi.PrettyMIDI(path)

    pitches = []
    note_count = 0
    for instrument in midi.instruments:
        if instrument.is_drum:
            continue
        for note in instrument.notes:
            pitches.append(note.pitch)
            note_count += 1

    if not pitches:
        return np.zeros(4)

    duration_seconds = midi.get_end_time()
    duration_beats = max(duration_seconds * bpm / 60.0, 1.0)

    avg_pitch = float(np.mean(pitches))
    pitch_range = float(max(pitches) - min(pitches))
    note_density = note_count / duration_beats

    return np.array([avg_pitch, pitch_range, note_density, float(bpm)])


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))