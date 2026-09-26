import random

from app.generation.sample import generate_raw_sequence
from app.generation.music_theory import (
    get_scale_notes,
    get_chord_progression,
    get_mood_params,
    get_raga_scale,
)


def generate_melody_ml(key: str, mood: str, bpm: int, duration_bars: int = 8, style: str = "western") -> dict:
    """
    Hybrid generation: the TCN provides melodic creativity (learned from
    real music), while this function enforces music-theory correctness
    as a post-processing constraint layer.
    """
    if style == "indian_folk":
        scale = get_raga_scale(mood)
    else:
        scale = get_scale_notes(key)

    mood_params = get_mood_params(mood)
    scale = [note + mood_params["register_shift"] for note in scale]
    progression = get_chord_progression(mood)
    v_min, v_max = mood_params["velocity_range"]

    target_beats = duration_bars * 4
    raw_sequence = generate_raw_sequence(min_duration_beats=target_beats)

    melody_notes = []
    chord_notes = []
    current_beat = 0.0
    beats_per_bar = 4

    for raw_pitch, raw_duration in raw_sequence:
        if current_beat >= target_beats:
            break

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
    candidates = [note + (12 * octave) for note in scale for octave in range(-2, 3)]
    return min(candidates, key=lambda c: abs(c - pitch))


def _build_triad(scale: list[int], root_degree: int) -> list[int]:
    n = len(scale)
    root = scale[root_degree % n]
    third = scale[(root_degree + 2) % n]
    fifth = scale[(root_degree + 4) % n]
    return [root, third, fifth]