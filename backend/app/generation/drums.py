# General MIDI percussion note numbers (channel 10 standard)
KICK = 36
SNARE = 38
CLOSED_HIHAT = 42
OPEN_HIHAT = 46
LOW_TOM = 41
HIGH_TOM = 43
CRASH = 49
RIDE = 51


def generate_drum_pattern(drum_style: str, duration_bars: int) -> list[dict]:
    """
    Generates a simple, rule-based drum pattern. Deliberately pattern-based
    rather than learned: rhythm-section conventions per genre/mood are
    well-established and don't need a trained model to reproduce.
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
            events.append({"pitch": SNARE, "start_beat": bar_start + 1, "duration_beats": 0.4, "velocity": 80})
            events.append({"pitch": KICK, "start_beat": bar_start + 2, "duration_beats": 0.4, "velocity": 90})
            events.append({"pitch": SNARE, "start_beat": bar_start + 3, "duration_beats": 0.4, "velocity": 80})

        elif drum_style == "war_drums":
            events.append({"pitch": LOW_TOM, "start_beat": bar_start + 0, "duration_beats": 0.5, "velocity": 110})
            events.append({"pitch": HIGH_TOM, "start_beat": bar_start + 1, "duration_beats": 0.5, "velocity": 95})
            events.append({"pitch": LOW_TOM, "start_beat": bar_start + 2, "duration_beats": 0.5, "velocity": 110})
            events.append({"pitch": HIGH_TOM, "start_beat": bar_start + 2.5, "duration_beats": 0.5, "velocity": 90})
            if bar == 0:
                events.append({"pitch": CRASH, "start_beat": bar_start, "duration_beats": 1.0, "velocity": 100})

        elif drum_style == "rock":
            for beat_half in range(beats_per_bar * 2):
                beat_pos = bar_start + beat_half * 0.5
                events.append({"pitch": CLOSED_HIHAT, "start_beat": beat_pos, "duration_beats": 0.4, "velocity": 80})
            events.append({"pitch": KICK, "start_beat": bar_start + 0, "duration_beats": 0.4, "velocity": 110})
            events.append({"pitch": SNARE, "start_beat": bar_start + 1, "duration_beats": 0.4, "velocity": 105})
            events.append({"pitch": KICK, "start_beat": bar_start + 2, "duration_beats": 0.4, "velocity": 110})
            events.append({"pitch": SNARE, "start_beat": bar_start + 3, "duration_beats": 0.4, "velocity": 105})
            if bar % 4 == 0:
                events.append({"pitch": CRASH, "start_beat": bar_start, "duration_beats": 1.0, "velocity": 110})

        elif drum_style == "swing":
            triplet_unit = 1.0 / 3.0
            for beat in range(beats_per_bar):
                events.append({"pitch": RIDE, "start_beat": bar_start + beat, "duration_beats": 0.5, "velocity": 85})
                events.append({"pitch": RIDE, "start_beat": bar_start + beat + 2 * triplet_unit, "duration_beats": 0.3, "velocity": 65})
            events.append({"pitch": KICK, "start_beat": bar_start + 0, "duration_beats": 0.3, "velocity": 60})
            events.append({"pitch": SNARE, "start_beat": bar_start + 2.5, "duration_beats": 0.3, "velocity": 55})

        elif drum_style == "hiphop":
            # Boom-bap: syncopated kick (on 1 and the "and" of 2), snare
            # on 3, and swung eighth-note hi-hats - the classic hip-hop
            # rhythmic signature, distinct from rock's straight backbeat.
            events.append({"pitch": KICK, "start_beat": bar_start + 0, "duration_beats": 0.4, "velocity": 105})
            events.append({"pitch": KICK, "start_beat": bar_start + 1.75, "duration_beats": 0.4, "velocity": 90})
            events.append({"pitch": SNARE, "start_beat": bar_start + 2, "duration_beats": 0.4, "velocity": 100})
            for beat in range(beats_per_bar):
                events.append({"pitch": CLOSED_HIHAT, "start_beat": bar_start + beat, "duration_beats": 0.3, "velocity": 70})
                events.append({"pitch": CLOSED_HIHAT, "start_beat": bar_start + beat + 0.67, "duration_beats": 0.3, "velocity": 55})

        elif drum_style == "lofi":
            # Relaxed, sparse boom-bap feel with soft dynamics and a
            # laid-back (slightly swung) hi-hat, evoking a "lo-fi beats
            # to study to" style rather than hiphop's punchier version.
            events.append({"pitch": KICK, "start_beat": bar_start + 0, "duration_beats": 0.4, "velocity": 70})
            events.append({"pitch": SNARE, "start_beat": bar_start + 2, "duration_beats": 0.4, "velocity": 60})
            for beat in range(beats_per_bar):
                events.append({"pitch": CLOSED_HIHAT, "start_beat": bar_start + beat + 0.6, "duration_beats": 0.3, "velocity": 45})

        elif drum_style == "sparse":
            events.append({"pitch": KICK, "start_beat": bar_start + 0, "duration_beats": 0.4, "velocity": 65})

    return events