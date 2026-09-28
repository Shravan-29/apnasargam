import os
import uuid

from app.generation.song_assembler import assemble_song
from app.generation.midi_export import notes_to_midi
from app.generation.intent_classifier import predict_mood_from_prompt
from app.db.session import SessionLocal
from app.models.project import Project

OUTPUT_DIR = "generated_midi"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def _save_project_record(user_id: int, project_name: str, mood: str, bpm: int, key: str, genre: str | None, filename: str):
    """
    Persists a Project row for the generated track so it shows up in the
    user's Dashboard. The worker process needs its own DB session here
    since it runs independently of any request/response cycle where
    FastAPI's get_db dependency would normally apply.
    """
    db = SessionLocal()
    try:
        project = Project(
            user_id=user_id,
            name=project_name,
            genre=genre,
            mood=mood,
            bpm=bpm,
            musical_key=key,
            midi_filename=filename,
        )
        db.add(project)
        db.commit()
    finally:
        db.close()


def generate_music_task(
    key: str, mood: str, bpm: int, project_name: str, user_id: int, genre: str | None = None, style: str = "western"
) -> dict:
    generation_result = assemble_song(key=key, mood=mood, bpm=bpm, style=style)

    filename = f"{uuid.uuid4()}.mid"
    output_path = os.path.join(OUTPUT_DIR, filename)
    notes_to_midi(generation_result, bpm=bpm, output_path=output_path, mood=mood, style=style, genre=genre)

    duration_seconds = (max(n["start_beat"] + n["duration_beats"] for n in generation_result["melody"]) * 60) / bpm

    _save_project_record(user_id, project_name, mood, bpm, key, genre, filename)

    return {
        "status": "completed",
        "project_name": project_name,
        "midi_file": filename,
        "note_count": len(generation_result["melody"]),
        "duration_seconds": round(duration_seconds, 1),
        "generation_method": "hybrid_tcn_ml_full_song",
    }


def generate_from_prompt_task(
    prompt: str, key: str, bpm: int, project_name: str, user_id: int, genre: str | None = None, style: str = "western"
) -> dict:
    predicted_mood = predict_mood_from_prompt(prompt)

    generation_result = assemble_song(key=key, mood=predicted_mood, bpm=bpm, style=style)

    filename = f"{uuid.uuid4()}.mid"
    output_path = os.path.join(OUTPUT_DIR, filename)
    notes_to_midi(generation_result, bpm=bpm, output_path=output_path, mood=predicted_mood, style=style, genre=genre)

    duration_seconds = (max(n["start_beat"] + n["duration_beats"] for n in generation_result["melody"]) * 60) / bpm

    _save_project_record(user_id, project_name, predicted_mood, bpm, key, genre, filename)

    return {
        "status": "completed",
        "project_name": project_name,
        "midi_file": filename,
        "note_count": len(generation_result["melody"]),
        "duration_seconds": round(duration_seconds, 1),
        "predicted_mood": predicted_mood,
        "generation_method": "nlp_intent_to_hybrid_tcn_full_song",
    }