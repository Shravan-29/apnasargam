import pytest

from app.generation.music_theory import (
    SCALES,
    MOOD_INSTRUMENTATION,
    GENRE_INSTRUMENTATION,
    MOOD_PARAMS,
    get_scale_notes,
    get_chord_progression,
    get_raga_scale,
    get_instrumentation,
)
from app.generation.drums import generate_drum_pattern

def test_unsupported_key_raises_a_clear_error():
    with pytest.raises(ValueError):
        get_scale_notes("H Sharp Major")

def test_every_scale_is_sorted_ascending():
    for name, notes in SCALES.items():
        assert notes == sorted(notes), f"{name} is not ascending"

def test_every_mood_has_params_and_instrumentation():
    for mood in MOOD_INSTRUMENTATION:
        assert mood in MOOD_PARAMS
        assert get_chord_progression(mood)

def test_every_mood_maps_to_a_raga_scale():
    for mood in MOOD_INSTRUMENTATION:
        assert len(get_raga_scale(mood)) >= 5

def test_genre_overrides_mood_instrumentation():
    rock = get_instrumentation("Calm", genre="Rock")
    assert rock == GENRE_INSTRUMENTATION["Rock"]
    assert rock != MOOD_INSTRUMENTATION["Calm"]

def test_unknown_genre_falls_back_to_mood():
    assert get_instrumentation("Calm", genre="Polka") == MOOD_INSTRUMENTATION["Calm"]

def test_no_genre_uses_mood():
    assert get_instrumentation("Epic") == MOOD_INSTRUMENTATION["Epic"]

def all_drum_styles():
    styles = {p["drum_style"] for p in MOOD_INSTRUMENTATION.values()}
    styles |= {p["drum_style"] for p in GENRE_INSTRUMENTATION.values()}
    return sorted(styles)

@pytest.mark.parametrize("style", all_drum_styles())
def test_every_configured_drum_style_is_implemented(style):
    events = generate_drum_pattern(style, duration_bars=4)
    if style == "none":
        assert events == []
    else:
        assert len(events) > 0, f"{style} is configured but produces no drum events"

@pytest.mark.parametrize("style", [s for s in all_drum_styles() if s != "none"])
def test_drum_events_stay_inside_the_requested_length(style):
    bars = 4
    for event in generate_drum_pattern(style, duration_bars=bars):
        assert 0 <= event["start_beat"] < bars * 4
        assert 1 <= event["velocity"] <= 127

def test_rock_and_swing_patterns_are_actually_different():
    rock = {(e["pitch"], e["start_beat"]) for e in generate_drum_pattern("rock", 1)}
    swing = {(e["pitch"], e["start_beat"]) for e in generate_drum_pattern("swing", 1)}
    assert rock != swing