import os
import uuid

from app.generation.model_generator import generate_melody_ml
from app.generation.midi_export import notes_to_midi

OUTPUT_DIR = "generated_midi"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_music_task(key: str, mood: str, bpm: int, project_name: str) -> dict:
    generation_result = generate_melody_ml(key=key, mood=mood, bpm=bpm, duration_bars=8, style="indian_folk")

    filename = f"{uuid.uuid4()}.mid"
    output_path = os.path.join(OUTPUT_DIR, filename)
    notes_to_midi(generation_result, bpm=bpm, output_path=output_path)

    return {
        "status": "completed",
        "project_name": project_name,
        "midi_file": filename,
        "note_count": len(generation_result["melody"]),
        "generation_method": "hybrid_tcn_ml",
    }