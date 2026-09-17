import random

from app.generation.music_theory import get_scale_notes, get_chord_progression, get_mood_params

def generate_melody(
    key: str,
    mood: str,
    bpm: int,
    duration_bars: int = 8,
) -> dict:
    """
    Generates a melody + chord accompaniment constrained to a musical key,
    following a mood-appropriate chord progression, register, rhythmic
    density, and dynamics.

    Returns {"melody": [...], "chords": [...]}
    """
    scale = get_scale_notes(key)
    progression = get_chord_progression(mood)
    mood_params = get_mood_params(mood)

    # apply register shift - dark/calm moods sit lower, energetic sits higher
    scale = [note + mood_params["register_shift"] for note in scale]

    density_to_duration_pool = {
        "sparse": [1.0, 1.0, 2.0, 2.0],
        "medium": [0.5, 1.0, 1.0, 1.0, 2.0],
        "dense": [0.25, 0.5, 0.5, 0.5, 1.0],
    }
    duration_pool = density_to_duration_pool[mood_params["density"]]
    v_min, v_max = mood_params["velocity_range"]

    melody_notes = []
    chord_notes = []
    current_beat = 0.0
    beats_per_bar = 4
    previous_pitch = scale[0]

    for bar in range(duration_bars):
        chord_degree = progression[bar % len(progression)]
        chord_root = scale[chord_degree]

        # accompaniment: hold a triad (root, third, fifth) for the whole bar
        triad = _build_triad(scale, chord_degree)
        for chord_pitch in triad:
            chord_notes.append({
                "pitch": chord_pitch - 12,
                "start_beat": current_beat,
                "duration_beats": beats_per_bar,
                "velocity": max(35, v_min - 20),
            })

        is_last_bar = bar == duration_bars - 1
        bar_start_beat = current_beat

        for beat_in_bar in range(beats_per_bar):
            is_last_note_in_piece = is_last_bar and beat_in_bar == beats_per_bar - 1

            if is_last_note_in_piece:
                note_pitch = chord_root
            else:
                note_pitch = _pick_smooth_note(scale, chord_root, previous_pitch)

            duration = random.choice(duration_pool)
            accent = 1.15 if beat_in_bar == 0 else 1.0
            velocity = min(127, int(random.randint(v_min, v_max) * accent))

            melody_notes.append({
                "pitch": note_pitch,
                "start_beat": current_beat,
                "duration_beats": duration,
                "velocity": velocity,
            })
            previous_pitch = note_pitch
            current_beat += duration

        current_beat = bar_start_beat + beats_per_bar

    return {"melody": melody_notes, "chords": chord_notes}


def _build_triad(scale: list[int], root_degree: int) -> list[int]:
    n = len(scale)
    root = scale[root_degree % n]
    third = scale[(root_degree + 2) % n]
    fifth = scale[(root_degree + 4) % n]
    return [root, third, fifth]


def _pick_smooth_note(scale: list[int], chord_root: int, previous_pitch: int) -> int:
    """
    Picks the next melody note weighted by two factors: closeness to the
    chord root (harmonic relevance) and closeness to the previous note
    (smooth melodic contour, avoids big leaps).
    """
    weights = []
    for note in scale:
        harmonic_distance = abs(note - chord_root)
        melodic_distance = abs(note - previous_pitch)
        weight = 1.0 / (1.0 + 0.6 * harmonic_distance + 0.4 * melodic_distance)
        weights.append(weight)

    return random.choices(scale, weights=weights, k=1)[0]