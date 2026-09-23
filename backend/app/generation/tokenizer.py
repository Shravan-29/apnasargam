from music21 import converter, note, chord
import os

def extract_notes_from_file(file_path: str) -> list[tuple[int, float]]:
    """
    Parses a MIDI file and extracts a sequence of (pitch, duration) pairs.
    Chords are simplified to their highest note (melody line focus).
    """
    score = converter.parse(file_path)
    elements = score.flatten().notes

    sequence = []
    for element in elements:
        if isinstance(element, note.Note):
            pitch = element.pitch.midi
        elif isinstance(element, chord.Chord):
            pitch = max(p.midi for p in element.pitches)  # take the top note
        else:
            continue

        duration = float(element.duration.quarterLength)
        sequence.append((pitch, duration))

    return sequence

def build_vocabulary(dataset_dir: str, max_files: int = 100) -> tuple[dict, dict]:
    """
    Scans a subset of the dataset and builds a vocabulary mapping each
    unique (pitch, duration) pair to a unique integer token.
    """
    all_files = [f for f in os.listdir(dataset_dir) if f.endswith(".mid")][:max_files]

    unique_tokens = set()
    for filename in all_files:
        file_path = os.path.join(dataset_dir, filename)
        try:
            sequence = extract_notes_from_file(file_path)
            unique_tokens.update(sequence)
        except Exception as e:
            print(f"Skipping {filename}: {e}")

    token_to_id = {token: idx for idx, token in enumerate(sorted(unique_tokens))}
    id_to_token = {idx: token for token, idx in token_to_id.items()}

    return token_to_id, id_to_token