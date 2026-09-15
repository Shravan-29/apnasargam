import random

from app.generation.music_theory import get_scale_notes, get_chord_progression


def generate_melody(
    key: str,
    mood: str,
    bpm: int,
    duration_bars: int = 8,
) -> list[dict]:
    """
    Generates a melody constrained to a musical key, following a
    mood-appropriate chord progression.

    Returns a list of note events: [{"pitch": int, "start_beat": float, "duration_beats": float}]
    """
    scale = get_scale_notes(key)
    progression = get_chord_progression(mood)

    notes = []
    current_beat = 0.0
    beats_per_bar = 4

    for bar in range(duration_bars):
        chord_degree = progression[bar % len(progression)]
        chord_root = scale[chord_degree]

        # generate 4 notes per bar (one per beat), weighted toward the chord tone
        for beat_in_bar in range(beats_per_bar):
            note_pitch = _pick_note_near_chord_tone(scale, chord_root)
            duration = _pick_duration()

            notes.append({
                "pitch": note_pitch,
                "start_beat": current_beat,
                "duration_beats": duration,
            })
            current_beat += duration

    return notes


def _pick_note_near_chord_tone(scale: list[int], chord_root: int) -> int:
    """
    Picks a note from the scale, weighted so that notes closer to the
    current chord's root are more likely — this keeps the melody sounding
    'in key' and harmonically related to the chord, rather than random.
    """
    weights = []
    for note in scale:
        distance = abs(note - chord_root)
        # inverse-distance weighting: closer notes get higher weight
        weight = 1.0 / (1.0 + distance)
        weights.append(weight)

    return random.choices(scale, weights=weights, k=1)[0]


def _pick_duration() -> float:
    """
    Randomly picks a note duration in beats, weighted toward
    quarter notes (1 beat) for rhythmic stability, with some
    eighth notes (0.5) and half notes (2) for variation.
    """
    options = [0.5, 1.0, 1.0, 1.0, 2.0]  # weighted list, quarter notes most common
    return random.choice(options)