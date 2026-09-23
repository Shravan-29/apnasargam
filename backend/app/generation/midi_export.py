# import pretty_midi


# def notes_to_midi(generation_result: dict, bpm: int, output_path: str) -> str:
#     midi = pretty_midi.PrettyMIDI(initial_tempo=bpm)
#     seconds_per_beat = 60.0 / bpm

#     sitar = pretty_midi.Instrument(program=104, name="Sitar")
#     shanai = pretty_midi.Instrument(program=111, name="Shanai")
#     harmonium = pretty_midi.Instrument(program=20, name="Harmonium")

#     for note_data in generation_result["melody"]:
#         start = note_data["start_beat"] * seconds_per_beat
#         end = start + (note_data["duration_beats"] * seconds_per_beat)
#         velocity = note_data.get("velocity", 90)

#         # Sitar carries the main melody at full velocity
#         sitar.notes.append(pretty_midi.Note(
#             velocity=velocity, pitch=note_data["pitch"], start=start, end=end,
#         ))

#         # Shanai doubles the melody quietly, for ensemble texture
#         shanai.notes.append(pretty_midi.Note(
#             velocity=max(30, velocity - 35), pitch=note_data["pitch"], start=start, end=end,
#         ))

#     for note_data in generation_result["chords"]:
#         start = note_data["start_beat"] * seconds_per_beat
#         end = start + (note_data["duration_beats"] * seconds_per_beat)
#         harmonium.notes.append(pretty_midi.Note(
#             velocity=note_data.get("velocity", 55), pitch=note_data["pitch"], start=start, end=end,
#         ))

#     midi.instruments.append(sitar)
#     midi.instruments.append(shanai)
#     midi.instruments.append(harmonium)
#     midi.write(output_path)
#     return output_path

import pretty_midi


def notes_to_midi(generation_result: dict, bpm: int, output_path: str) -> str:
    midi = pretty_midi.PrettyMIDI(initial_tempo=bpm)
    seconds_per_beat = 60.0 / bpm

    flute = pretty_midi.Instrument(program=73, name="Flute")
    sitar = pretty_midi.Instrument(program=104, name="Sitar")
    harmonium = pretty_midi.Instrument(program=20, name="Harmonium")

    for note_data in generation_result["melody"]:
        start = note_data["start_beat"] * seconds_per_beat
        end = start + (note_data["duration_beats"] * seconds_per_beat)
        velocity = note_data.get("velocity", 90)

        # Flute carries the main melody, full volume - the "Krishna bansuri" lead
        flute.notes.append(pretty_midi.Note(
            velocity=velocity, pitch=note_data["pitch"], start=start, end=end,
        ))

        # Sitar doubles softly underneath for texture
        sitar.notes.append(pretty_midi.Note(
            velocity=max(30, velocity - 40), pitch=note_data["pitch"], start=start, end=end,
        ))

    for note_data in generation_result["chords"]:
        start = note_data["start_beat"] * seconds_per_beat
        end = start + (note_data["duration_beats"] * seconds_per_beat)
        harmonium.notes.append(pretty_midi.Note(
            velocity=note_data.get("velocity", 55), pitch=note_data["pitch"], start=start, end=end,
        ))

    midi.instruments.append(flute)
    midi.instruments.append(sitar)
    midi.instruments.append(harmonium)
    midi.write(output_path)
    return output_path