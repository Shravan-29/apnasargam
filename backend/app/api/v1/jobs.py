from fastapi import APIRouter, Depends
from rq.job import Job

from app.core.queue import generation_queue, redis_conn
from app.core.security import get_current_user
from app.models.user import User
from app.jobs.tasks import dummy_generation_task

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])


@router.post("/test-generate")
def enqueue_test_job(
    project_name: str,
    current_user: User = Depends(get_current_user),
):
    job = generation_queue.enqueue(dummy_generation_task, project_name)
    return {"job_id": job.id, "status": "queued"}


@router.get("/{job_id}")
def get_job_status(job_id: str, current_user: User = Depends(get_current_user)):
    job = Job.fetch(job_id, connection=redis_conn)
    return {
        "job_id": job.id,
        "status": job.get_status(),
        "result": job.result,
    }