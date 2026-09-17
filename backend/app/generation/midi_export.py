import pretty_midi


def notes_to_midi(generation_result: dict, bpm: int, output_path: str) -> str:
    midi = pretty_midi.PrettyMIDI(initial_tempo=bpm)
    seconds_per_beat = 60.0 / bpm

    melody_instrument = pretty_midi.Instrument(program=0, name="Melody")  # Piano
    chord_instrument = pretty_midi.Instrument(program=48, name="Chords")  # Strings Ensemble

    for note_data in generation_result["melody"]:
        start = note_data["start_beat"] * seconds_per_beat
        end = start + (note_data["duration_beats"] * seconds_per_beat)
        melody_instrument.notes.append(pretty_midi.Note(
            velocity=note_data.get("velocity", 90),
            pitch=note_data["pitch"],
            start=start,
            end=end,
        ))

    for note_data in generation_result["chords"]:
        start = note_data["start_beat"] * seconds_per_beat
        end = start + (note_data["duration_beats"] * seconds_per_beat)
        chord_instrument.notes.append(pretty_midi.Note(
            velocity=note_data.get("velocity", 55),
            pitch=note_data["pitch"],
            start=start,
            end=end,
        ))

    midi.instruments.append(melody_instrument)
    midi.instruments.append(chord_instrument)
    midi.write(output_path)
    return output_path