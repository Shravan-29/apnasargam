from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from rq.job import Job
from sqlalchemy.orm import Session
import os

from app.core.queue import generation_queue, redis_conn
from app.core.security import get_current_user, decode_access_token
from app.db.session import get_db
from app.models.user import User
from app.jobs.tasks import generate_music_task
from app.schemas.generation import GenerationRequest

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])


@router.post("/generate")
def enqueue_generation(
    request: GenerationRequest,
    current_user: User = Depends(get_current_user),
):
    job = generation_queue.enqueue(
        generate_music_task,
        key=request.key,
        mood=request.mood,
        bpm=request.bpm,
        project_name=request.project_name,
    )
    return {"job_id": job.id, "status": "queued"}


@router.get("/{job_id}")
def get_job_status(job_id: str, current_user: User = Depends(get_current_user)):
    try:
        job = Job.fetch(job_id, connection=redis_conn)
    except Exception:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "job_id": job.id,
        "status": job.get_status(),
        "result": job.result,
    }


@router.get("/{job_id}/midi")
def download_midi(
    job_id: str,
    token: str,
    db: Session = Depends(get_db),
):
    # NOTE: this endpoint takes the token as a query param instead of an
    # Authorization header, because the <midi-player> web component fetches
    # this URL internally and cannot attach custom headers. Browsers allow
    # media elements to set a `src` URL but not custom request headers.
    try:
        user_id = decode_access_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    try:
        job = Job.fetch(job_id, connection=redis_conn)
    except Exception:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.get_status() != "finished" or not job.result:
        raise HTTPException(status_code=400, detail="Job not finished yet")

    filename = job.result.get("midi_file")
    file_path = os.path.join("generated_midi", filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="MIDI file not found on disk")

    return FileResponse(file_path, media_type="audio/midi", filename=filename)