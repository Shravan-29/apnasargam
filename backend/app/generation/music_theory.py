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
CHORD_PROGRESSIONS = {
    "pop": [0, 4, 5, 3],
    "sad": [5, 3, 0, 4],
    "cinematic": [0, 5, 3, 4],
    "tense": [5, 4, 0, 0],
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

MOOD_PARAMS = {
    "Dark": {"register_shift": -12, "density": "sparse", "velocity_range": (60, 85)},
    "Uplifting": {"register_shift": 0, "density": "medium", "velocity_range": (85, 110)},
    "Calm": {"register_shift": -5, "density": "sparse", "velocity_range": (55, 75)},
    "Energetic": {"register_shift": 5, "density": "dense", "velocity_range": (90, 115)},
    "Melancholic": {"register_shift": -7, "density": "sparse", "velocity_range": (50, 70)},
    "Epic": {"register_shift": 0, "density": "medium", "velocity_range": (95, 120)},
    "Romantic": {"register_shift": -3, "density": "medium", "velocity_range": (65, 90)},
}

# Indian classical/folk raga scales, expressed as MIDI pitch numbers.
# These are structurally different from Western major/minor scales,
# which gives generated melodies a distinctly Indian folk character.
RAGA_SCALES = {
    "Yaman": [60, 62, 64, 66, 67, 69, 71, 72],
    "Bhairav": [60, 61, 64, 65, 67, 68, 71, 72],
    "Bhupali": [60, 62, 64, 67, 69, 72, 74, 76],
}

RAGA_MOOD_MAP = {
    "Romantic": "Yaman",
    "Calm": "Bhupali",
    "Uplifting": "Bhupali",
    "Melancholic": "Bhairav",
    "Dark": "Bhairav",
    "Epic": "Yaman",
    "Energetic": "Bhupali",
}


def get_scale_notes(key: str) -> list[int]:
    if key not in SCALES:
        raise ValueError(f"Unsupported key: {key}. Supported: {list(SCALES.keys())}")
    return SCALES[key]


def get_chord_progression(mood: str) -> list[int]:
    progression_name = MOOD_TO_PROGRESSION.get(mood, "pop")
    return CHORD_PROGRESSIONS[progression_name]


def get_mood_params(mood: str) -> dict:
    return MOOD_PARAMS.get(mood, MOOD_PARAMS["Uplifting"])


def get_raga_scale(mood: str) -> list[int]:
    raga_name = RAGA_MOOD_MAP.get(mood, "Bhupali")
    return RAGA_SCALES[raga_name]

MOOD_INSTRUMENTATION = {
    "Dark":        {"melody_program": 44, "harmony_program": 52, "drum_style": "none"},
    "Uplifting":   {"melody_program": 0,  "harmony_program": 48, "drum_style": "medium"},
    "Calm":        {"melody_program": 73, "harmony_program": 20, "drum_style": "none"},
    "Energetic":   {"melody_program": 81, "harmony_program": 38, "drum_style": "four_on_floor"},
    "Melancholic": {"melody_program": 73, "harmony_program": 20, "drum_style": "none"},
    "Epic":        {"melody_program": 56, "harmony_program": 48, "drum_style": "war_drums"},
    "Romantic":    {"melody_program": 73, "harmony_program": 20, "drum_style": "none"},
}

def get_instrumentation(mood: str) -> dict:
    return MOOD_INSTRUMENTATION.get(mood, MOOD_INSTRUMENTATION["Uplifting"])