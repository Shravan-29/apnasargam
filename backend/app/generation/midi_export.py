import pretty_midi


def notes_to_midi(notes: list[dict], bpm: int, output_path: str) -> str:
    """
    Converts a list of note events into a playable MIDI file.

    notes: list of {"pitch": int, "start_beat": float, "duration_beats": float}
    bpm: beats per minute, used to convert beats into real seconds
    output_path: file path to save the .mid file
    """
    midi = pretty_midi.PrettyMIDI(initial_tempo=bpm)
    instrument = pretty_midi.Instrument(program=0)  # program 0 = Acoustic Grand Piano

    seconds_per_beat = 60.0 / bpm

    for note_data in notes:
        start_time = note_data["start_beat"] * seconds_per_beat
        end_time = start_time + (note_data["duration_beats"] * seconds_per_beat)

        note = pretty_midi.Note(
            velocity=90,
            pitch=note_data["pitch"],
            start=start_time,
            end=end_time,
        )
        instrument.notes.append(note)

    midi.instruments.append(instrument)
    midi.write(output_path)
    return output_path