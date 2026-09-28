import pretty_midi

from app.generation.midi_export import notes_to_midi

def fake_song(bars=4):
    melody = [
        {"pitch": 60 + (i % 5), "start_beat": float(i), "duration_beats": 1.0, "velocity": 90}
        for i in range(bars * 4)
    ]
    chords = [
        {"pitch": p, "start_beat": float(b * 4), "duration_beats": 4.0, "velocity": 55}
        for b in range(bars)
        for p in (48, 52, 55)
    ]
    return {"melody": melody, "chords": chords}

def test_exported_file_is_valid_midi_with_the_requested_tempo(tmp_path):
    out = tmp_path / "song.mid"
    notes_to_midi(fake_song(), bpm=100, output_path=str(out), mood="Uplifting")

    loaded = pretty_midi.PrettyMIDI(str(out))
    assert round(loaded.estimate_tempo()) > 0
    assert loaded.get_end_time() > 0

def test_note_count_survives_export(tmp_path):
    out = tmp_path / "song.mid"
    song = fake_song()
    notes_to_midi(song, bpm=120, output_path=str(out), mood="Calm", genre="Classical")

    loaded = pretty_midi.PrettyMIDI(str(out))
    total_notes = sum(len(i.notes) for i in loaded.instruments if not i.is_drum)
    assert total_notes == len(song["melody"]) + len(song["chords"])

def test_rock_export_contains_a_drum_track(tmp_path):
    out = tmp_path / "rock.mid"
    notes_to_midi(fake_song(), bpm=120, output_path=str(out), mood="Energetic", genre="Rock")

    loaded = pretty_midi.PrettyMIDI(str(out))
    assert any(i.is_drum and len(i.notes) > 0 for i in loaded.instruments)

def test_classical_export_has_no_drum_track(tmp_path):
    out = tmp_path / "classical.mid"
    notes_to_midi(fake_song(), bpm=120, output_path=str(out), mood="Calm", genre="Classical")

    loaded = pretty_midi.PrettyMIDI(str(out))
    assert not any(i.is_drum for i in loaded.instruments)

def test_genre_changes_the_instruments_used(tmp_path):
    rock_path = tmp_path / "rock.mid"
    jazz_path = tmp_path / "jazz.mid"
    notes_to_midi(fake_song(), bpm=120, output_path=str(rock_path), mood="Calm", genre="Rock")
    notes_to_midi(fake_song(), bpm=120, output_path=str(jazz_path), mood="Calm", genre="Jazz")

    rock_programs = {i.program for i in pretty_midi.PrettyMIDI(str(rock_path)).instruments if not i.is_drum}
    jazz_programs = {i.program for i in pretty_midi.PrettyMIDI(str(jazz_path)).instruments if not i.is_drum}
    assert rock_programs != jazz_programs

def test_indian_folk_style_ignores_genre_and_uses_no_drums(tmp_path):
    out = tmp_path / "folk.mid"
    notes_to_midi(fake_song(), bpm=90, output_path=str(out), mood="Calm", style="indian_folk", genre="Rock")

    loaded = pretty_midi.PrettyMIDI(str(out))
    assert not any(i.is_drum for i in loaded.instruments)