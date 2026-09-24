import pretty_midi

from app.generation.music_theory import get_instrumentation
from app.generation.drums import generate_drum_pattern

# Fixed ethnic ensemble used specifically for the "indian_folk" style,
# independent of mood - the raga-based generation already encodes mood
# through scale choice, so instrumentation stays consistent for
# authenticity (no drums, to preserve the traditional feel).
INDIAN_FOLK_PROFILE = {"melody_program": 73, "harmony_program": 20, "drum_style": "none"}

def notes_to_midi(
    generation_result: dict,
    bpm: int,
    output_path: str,
    mood: str = "Uplifting",
    style: str = "western",
) -> str:
    profile = INDIAN_FOLK_PROFILE if style == "indian_folk" else get_instrumentation(mood)

    midi = pretty_midi.PrettyMIDI(initial_tempo=bpm)
    seconds_per_beat = 60.0 / bpm

    melody_instrument = pretty_midi.Instrument(program=profile["melody_program"], name="Melody")
    harmony_instrument = pretty_midi.Instrument(program=profile["harmony_program"], name="Harmony")
    drum_instrument = pretty_midi.Instrument(program=0, is_drum=True, name="Drums")

    for note_data in generation_result["melody"]:
        start = note_data["start_beat"] * seconds_per_beat
        end = start + (note_data["duration_beats"] * seconds_per_beat)
        melody_instrument.notes.append(pretty_midi.Note(
            velocity=note_data.get("velocity", 90), pitch=note_data["pitch"], start=start, end=end,
        ))

    for note_data in generation_result["chords"]:
        start = note_data["start_beat"] * seconds_per_beat
        end = start + (note_data["duration_beats"] * seconds_per_beat)
        harmony_instrument.notes.append(pretty_midi.Note(
            velocity=note_data.get("velocity", 55), pitch=note_data["pitch"], start=start, end=end,
        ))

    duration_bars = int(max(n["start_beat"] + n["duration_beats"] for n in generation_result["melody"]) // 4) + 1
    drum_events = generate_drum_pattern(profile["drum_style"], duration_bars)
    for drum_data in drum_events:
        start = drum_data["start_beat"] * seconds_per_beat
        end = start + (drum_data["duration_beats"] * seconds_per_beat)
        drum_instrument.notes.append(pretty_midi.Note(
            velocity=drum_data["velocity"], pitch=drum_data["pitch"], start=start, end=end,
        ))

    midi.instruments.append(melody_instrument)
    midi.instruments.append(harmony_instrument)
    if drum_events:
        midi.instruments.append(drum_instrument)

    midi.write(output_path)
    return output_path