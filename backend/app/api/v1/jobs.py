from fastapi import APIRouter, Depends, HTTPException
from rq.job import Job

from app.core.queue import generation_queue, redis_conn
from app.core.security import get_current_user
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