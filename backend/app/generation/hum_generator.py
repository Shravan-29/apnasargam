import random

from app.generation.sample import generate_raw_sequence, get_vocabulary
from app.generation.music_theory import get_mood_params

CONTINUATION_BARS = 16  # fixed length; this mode is not integrated with
                         # the multi-section song assembler, by design,
                         # to keep the hum-seeding logic self-contained


def generate_melody_from_hum(
    hum_notes: list[tuple[int, float, float]],
    bpm: int,
    mood: str,
) -> dict:
    """
    Converts detected hum notes (midi_pitch, start_seconds, duration_seconds)
    into melody note events, snapping each to the nearest token the TCN
    was actually trained on, then uses the hum as a seed context so the
    model continues in a similar melodic style rather than ignoring it.

    No chord/harmony track is generated here (hum_generator returns an
    empty "chords" list) - this mode is melody-only by design, since the
    hum doesn't imply a chosen key or chord progression the way the
    structured/prompt modes do.
    """
    token_to_id, id_to_token = get_vocabulary()
    vocab_tokens = list(token_to_id.keys())

    def snap_to_vocab(pitch: int, duration: float) -> tuple[int, float]:
        return min(vocab_tokens, key=lambda t: abs(t[0] - pitch) * 2 + abs(t[1] - duration))

    mood_params = get_mood_params(mood)
    v_min, v_max = mood_params["velocity_range"]

    melody_notes = []
    seed_token_ids = []
    hum_end_beat = 0.0

    for pitch, start_sec, duration_sec in hum_notes:
        start_beat = start_sec * bpm / 60.0
        raw_duration_beat = max(duration_sec * bpm / 60.0, 0.25)
        snapped_pitch, snapped_duration = snap_to_vocab(pitch, raw_duration_beat)

        melody_notes.append({
            "pitch": snapped_pitch,
            "start_beat": start_beat,
            "duration_beats": snapped_duration,
            "velocity": random.randint(v_min, v_max),
        })
        seed_token_ids.append(token_to_id[(snapped_pitch, snapped_duration)])
        hum_end_beat = max(hum_end_beat, start_beat + snapped_duration)

    target_beats = CONTINUATION_BARS * 4
    remaining_beats = max(0.0, target_beats - hum_end_beat)

    if remaining_beats > 0 and seed_token_ids:
        continuation = generate_raw_sequence(
            min_duration_beats=remaining_beats,
            seed_tokens=seed_token_ids[-64:],
        )
        cursor = hum_end_beat
        for pitch, duration in continuation:
            melody_notes.append({
                "pitch": pitch,
                "start_beat": cursor,
                "duration_beats": duration,
                "velocity": random.randint(v_min, v_max),
            })
            cursor += duration

    return {"melody": melody_notes, "chords": []}