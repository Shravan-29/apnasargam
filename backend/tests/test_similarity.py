import numpy as np
import pretty_midi
import pytest

from app.generation import similarity
from app.generation.similarity import extract_feature_vector, similarity_score


def vec(avg_pitch, pitch_range, density, bpm):
    return np.array([avg_pitch, pitch_range, density, float(bpm)])


CALM_A = vec(55, 24, 1.75, 78)
CALM_B = vec(57, 24, 1.85, 85)
ENERGETIC = vec(71, 30, 3.75, 135)


def test_identical_tracks_score_one():
    assert similarity_score(CALM_A, CALM_A) == pytest.approx(1.0)


def test_score_is_symmetric_and_bounded():
    s1 = similarity_score(CALM_A, ENERGETIC)
    s2 = similarity_score(ENERGETIC, CALM_A)
    assert s1 == pytest.approx(s2)
    assert 0.0 <= s1 <= 1.0


def test_similar_tracks_outscore_different_ones():
    assert similarity_score(CALM_A, CALM_B) > similarity_score(CALM_A, ENERGETIC)


def test_regression_dissimilar_tracks_no_longer_score_near_100_percent():
    """
    The first version used cosine similarity on raw features and scored a
    calm track vs an energetic one at about 99%. A calm and an energetic
    track must now be clearly apart, and a close pair clearly together.
    """
    assert similarity_score(CALM_A, ENERGETIC) < 0.2
    assert similarity_score(CALM_A, CALM_B) > 0.8


def test_typical_tracks_still_match_their_near_duplicates():
    """A centered cosine version scored this pair at about 0 (undefined near the origin)."""
    assert similarity_score(vec(62, 26, 2.0, 100), vec(63, 26, 2.1, 102)) > 0.9


def test_empty_track_vector_matches_nothing():
    assert similarity_score(np.zeros(4), CALM_A) < 0.01


def write_midi(path, bpm, pitches, with_drums=False):
    pm = pretty_midi.PrettyMIDI(initial_tempo=bpm)
    inst = pretty_midi.Instrument(program=0)
    beat = 60.0 / bpm
    for i, p in enumerate(pitches):
        inst.notes.append(pretty_midi.Note(90, p, i * beat, (i + 1) * beat))
    pm.instruments.append(inst)
    if with_drums:
        drums = pretty_midi.Instrument(program=0, is_drum=True)
        for i in range(len(pitches)):
            drums.notes.append(pretty_midi.Note(100, 36, i * beat, i * beat + 0.1))
        pm.instruments.append(drums)
    pm.write(str(path))


@pytest.fixture()
def midi_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(similarity, "MIDI_DIR", str(tmp_path))
    return tmp_path


def test_extracted_features_match_a_track_with_known_content(midi_dir):
    # 8 one-beat notes alternating between pitch 60 and 72 at 120 BPM
    write_midi(midi_dir / "known.mid", 120, [60, 72] * 4)
    avg_pitch, pitch_range, density, bpm = extract_feature_vector("known.mid", 120)

    assert avg_pitch == pytest.approx(66.0)
    assert pitch_range == pytest.approx(12.0)
    assert density == pytest.approx(1.0, abs=0.05)
    assert bpm == 120.0


def test_drum_track_is_ignored_in_the_features(midi_dir):
    write_midi(midi_dir / "plain.mid", 120, [60, 72] * 4)
    write_midi(midi_dir / "drums.mid", 120, [60, 72] * 4, with_drums=True)

    assert np.allclose(extract_feature_vector("plain.mid", 120), extract_feature_vector("drums.mid", 120), atol=0.05)


def test_midi_with_only_drums_gives_a_zero_vector(midi_dir):
    pm = pretty_midi.PrettyMIDI(initial_tempo=120)
    drums = pretty_midi.Instrument(program=0, is_drum=True)
    drums.notes.append(pretty_midi.Note(100, 36, 0.0, 0.2))
    pm.instruments.append(drums)
    pm.write(str(midi_dir / "only_drums.mid"))

    assert np.allclose(extract_feature_vector("only_drums.mid", 120), np.zeros(4))