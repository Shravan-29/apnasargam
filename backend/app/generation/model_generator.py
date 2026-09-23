from app.generation.sample import generate_raw_sequence
from app.generation.music_theory import get_scale_notes, get_chord_progression, get_mood_params


def generate_melody_ml(key: str, mood: str, bpm: int, duration_bars: int = 8, style: str = "western") -> dict:
    """
    Hybrid generation: the TCN provides melodic creativity (learned from
    real music), while this function enforces music-theory correctness
    as a post-processing constraint layer. This is the core hybrid
    neuro-symbolic design: the model isn't trusted to get music theory
    right on its own, its raw output is corrected to fit the requested
    key and mood.
    """
    scale = get_scale_notes(key)
    if style == "indian_folk":
     from app.generation.music_theory import get_raga_scale
    scale = get_raga_scale(mood)
    mood_params = get_mood_params(mood)
    scale = [note + mood_params["register_shift"] for note in scale]
    progression = get_chord_progression(mood)
    v_min, v_max = mood_params["velocity_range"]

    target_beats = duration_bars * 4
    raw_sequence = generate_raw_sequence(num_events=target_beats * 2)  # generate extra, trim to length

    melody_notes = []
    chord_notes = []
    current_beat = 0.0
    beats_per_bar = 4

    import random

    for raw_pitch, raw_duration in raw_sequence:
        if current_beat >= target_beats:
            break

        # constraint layer: snap the model's raw pitch to the nearest
        # note actually in the requested scale, searching across octaves
        snapped_pitch = _snap_to_scale(raw_pitch, scale)

        bar_index = int(current_beat // beats_per_bar) % len(progression)
        beat_in_bar = current_beat % beats_per_bar

        velocity = random.randint(v_min, v_max)
        if beat_in_bar == 0:
            velocity = min(127, int(velocity * 1.15))

        melody_notes.append({
            "pitch": snapped_pitch,
            "start_beat": current_beat,
            "duration_beats": raw_duration,
            "velocity": velocity,
        })
        current_beat += raw_duration

    # accompaniment: same rule-based triads as before, per bar
    bar_start = 0.0
    while bar_start < target_beats:
        bar_index = int(bar_start // beats_per_bar) % len(progression)
        chord_degree = progression[bar_index]
        triad = _build_triad(scale, chord_degree)
        for pitch in triad:
            chord_notes.append({
                "pitch": pitch - 12,
                "start_beat": bar_start,
                "duration_beats": beats_per_bar,
                "velocity": max(35, v_min - 20),
            })
        bar_start += beats_per_bar

    return {"melody": melody_notes, "chords": chord_notes}


def _snap_to_scale(pitch: int, scale: list[int]) -> int:
    """Finds the closest note to `pitch` across multiple octaves of the given scale."""
    candidates = [note + (12 * octave) for note in scale for octave in range(-2, 3)]
    return min(candidates, key=lambda c: abs(c - pitch))


def _build_triad(scale: list[int], root_degree: int) -> list[int]:
    n = len(scale)
    root = scale[root_degree % n]
    third = scale[(root_degree + 2) % n]
    fifth = scale[(root_degree + 4) % n]
    return [root, third, fifth]