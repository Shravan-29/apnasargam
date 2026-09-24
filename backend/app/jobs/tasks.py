import os
import uuid

from app.generation.model_generator import generate_melody_ml
from app.generation.midi_export import notes_to_midi
from app.generation.intent_classifier import predict_mood_from_prompt

OUTPUT_DIR = "generated_midi"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_music_task(key: str, mood: str, bpm: int, project_name: str) -> dict:
    generation_result = generate_melody_ml(key=key, mood=mood, bpm=bpm, duration_bars=8)

    filename = f"{uuid.uuid4()}.mid"
    output_path = os.path.join(OUTPUT_DIR, filename)
    notes_to_midi(generation_result, bpm=bpm, output_path=output_path, mood=mood, style="western")

    return {
        "status": "completed",
        "project_name": project_name,
        "midi_file": filename,
        "note_count": len(generation_result["melody"]),
        "generation_method": "hybrid_tcn_ml",
    }

def generate_from_prompt_task(prompt: str, key: str, bpm: int, project_name: str) -> dict:
    predicted_mood = predict_mood_from_prompt(prompt)

    generation_result = generate_melody_ml(key=key, mood=predicted_mood, bpm=bpm, duration_bars=8)

    filename = f"{uuid.uuid4()}.mid"
    output_path = os.path.join(OUTPUT_DIR, filename)
    notes_to_midi(generation_result, bpm=bpm, output_path=output_path, mood=predicted_mood, style="western")

    return {
        "status": "completed",
        "project_name": project_name,
        "midi_file": filename,
        "note_count": len(generation_result["melody"]),
        "predicted_mood": predicted_mood,
        "generation_method": "nlp_intent_to_hybrid_tcn",
    }