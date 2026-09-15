import os
import uuid

from app.generation.melody_generator import generate_melody
from app.generation.midi_export import notes_to_midi

OUTPUT_DIR = "generated_midi"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_music_task(key: str, mood: str, bpm: int, project_name: str) -> dict:
    """
    The real AI/generation task — replaces the earlier dummy placeholder.
    Runs inside the RQ worker process, not the API request thread.
    """
    notes = generate_melody(key=key, mood=mood, bpm=bpm, duration_bars=8)

    filename = f"{uuid.uuid4()}.mid"
    output_path = os.path.join(OUTPUT_DIR, filename)
    notes_to_midi(notes, bpm=bpm, output_path=output_path)

    return {
        "status": "completed",
        "project_name": project_name,
        "midi_file": filename,
        "note_count": len(notes),
    }