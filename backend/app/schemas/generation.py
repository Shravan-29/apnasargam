from pydantic import BaseModel

class GenerationRequest(BaseModel):
    project_name: str
    key: str
    mood: str
    bpm: int = 120

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    result: dict | None = None