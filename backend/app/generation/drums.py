# General MIDI percussion note numbers (channel 10 standard)
KICK = 36
SNARE = 38
CLOSED_HIHAT = 42

def generate_drum_pattern(drum_style: str, duration_bars: int) -> list[dict]:
    """
    Generates a simple, rule-based drum pattern. This is deliberately
    pattern-based rather than learned: the project's ML focus is
    melodic/harmonic generation (TCN), while rhythm-section patterns
    follow well-established genre conventions that don't need a
    trained model to reproduce correctly.
    """
    if drum_style == "none":
        return []

    beats_per_bar = 4
    events = []

    for bar in range(duration_bars):
        bar_start = bar * beats_per_bar

        if drum_style == "four_on_floor":
            for beat in range(beats_per_bar):
                events.append({"pitch": KICK, "start_beat": bar_start + beat, "duration_beats": 0.4, "velocity": 105})
                events.append({"pitch": CLOSED_HIHAT, "start_beat": bar_start + beat + 0.5, "duration_beats": 0.4, "velocity": 75})
            events.append({"pitch": SNARE, "start_beat": bar_start + 2, "duration_beats": 0.4, "velocity": 100})

        elif drum_style == "medium":
            events.append({"pitch": KICK, "start_beat": bar_start + 0, "duration_beats": 0.4, "velocity": 90})
            events.append({"pitch": SNARE, "start_beat": bar_start + 1, "duration_beats": 0.4, "velocity": 85})
            events.append({"pitch": KICK, "start_beat": bar_start + 2, "duration_beats": 0.4, "velocity": 90})
            events.append({"pitch": SNARE, "start_beat": bar_start + 3, "duration_beats": 0.4, "velocity": 85})

        elif drum_style == "war_drums":
            events.append({"pitch": LOW_TOM, "start_beat": bar_start + 0, "duration_beats": 0.5, "velocity": 110})
            events.append({"pitch": HIGH_TOM, "start_beat": bar_start + 1, "duration_beats": 0.5, "velocity": 95})
            events.append({"pitch": LOW_TOM, "start_beat": bar_start + 2, "duration_beats": 0.5, "velocity": 110})
            events.append({"pitch": HIGH_TOM, "start_beat": bar_start + 2.5, "duration_beats": 0.5, "velocity": 90})
            if bar == 0:
                events.append({"pitch": CRASH, "start_beat": bar_start, "duration_beats": 1.0, "velocity": 100})    

        elif drum_style == "sparse":
            events.append({"pitch": KICK, "start_beat": bar_start + 0, "duration_beats": 0.4, "velocity": 65})

    return events