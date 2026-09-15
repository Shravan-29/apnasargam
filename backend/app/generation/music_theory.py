# Notes are represented as MIDI pitch numbers.
# Middle C (C4) = 60 in MIDI numbering.

SCALES = {
    "C Major": [60, 62, 64, 65, 67, 69, 71, 72],
    "A Minor": [57, 59, 60, 62, 64, 65, 67, 69],
    "D Minor": [62, 64, 65, 67, 69, 70, 72, 74],
    "F# Minor": [66, 68, 69, 71, 73, 74, 76, 78],
    "G Major": [67, 69, 71, 72, 74, 76, 78, 79],
}

# Chord progressions expressed as scale-degree indices (0-indexed into SCALES list)
# e.g. "I-V-vi-IV" is a very common pop progression
CHORD_PROGRESSIONS = {
    "pop": [0, 4, 5, 3],       # I - V - vi - IV
    "sad": [5, 3, 0, 4],       # vi - IV - I - V
    "cinematic": [0, 5, 3, 4], # I - vi - IV - V
    "tense": [5, 4, 0, 0],     # vi - V - I - I
}

MOOD_TO_PROGRESSION = {
    "Dark": "tense",
    "Melancholic": "sad",
    "Uplifting": "pop",
    "Epic": "cinematic",
    "Calm": "pop",
    "Energetic": "pop",
    "Romantic": "sad",
}


def get_scale_notes(key: str) -> list[int]:
    if key not in SCALES:
        raise ValueError(f"Unsupported key: {key}. Supported: {list(SCALES.keys())}")
    return SCALES[key]


def get_chord_progression(mood: str) -> list[int]:
    progression_name = MOOD_TO_PROGRESSION.get(mood, "pop")
    return CHORD_PROGRESSIONS[progression_name]