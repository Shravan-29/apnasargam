from app.generation.model_generator import generate_melody_ml

# Standard verse-chorus song structure, in bars per section.
# Repeated section names (verse, chorus) reuse the same generated
# content rather than generating fresh material each time - this
# mirrors how real songs repeat a chorus, and avoids redundant model
# inference for structurally-identical slots.
SONG_STRUCTURE = [
    ("intro", 4),
    ("verse", 8),
    ("chorus", 8),
    ("verse", 8),
    ("chorus", 8),
    ("outro", 4),
]


def assemble_song(key: str, mood: str, bpm: int, style: str = "western") -> dict:
    """
    Builds a full ~1-2 minute song by generating each UNIQUE section once
    (intro, verse, chorus, outro) via the hybrid TCN + constraint pipeline,
    then arranging them into the structure above. This solves two problems
    at once: (1) long single-pass generation degrades in coherence for
    sequence models, so generating short, independent, coherent sections
    and composing them avoids that; (2) reusing repeated sections verbatim
    cuts model-inference calls roughly in half versus generating every
    bar fresh.
    """
    unique_sections = {}
    for name, bars in SONG_STRUCTURE:
        if name not in unique_sections:
            unique_sections[name] = generate_melody_ml(
                key=key, mood=mood, bpm=bpm, duration_bars=bars, style=style
            )

    melody_notes = []
    chord_notes = []
    beat_offset = 0.0

    for name, bars in SONG_STRUCTURE:
        section = unique_sections[name]
        for note in section["melody"]:
            melody_notes.append({**note, "start_beat": note["start_beat"] + beat_offset})
        for note in section["chords"]:
            chord_notes.append({**note, "start_beat": note["start_beat"] + beat_offset})
        beat_offset += bars * 4

    return {"melody": melody_notes, "chords": chord_notes}