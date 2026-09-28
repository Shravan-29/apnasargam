from pydantic import BaseModel


class GenerationRequest(BaseModel):
    project_name: str
    key: str
    mood: str
    bpm: int = 120
    genre: str | None = None
    style: str = "western"


class PromptGenerationRequest(BaseModel):
    project_name: str
    prompt: str
    key: str = "C Major"
    bpm: int = 110
    genre: str | None = None
    style: str = "western"


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    result: dict | None = None