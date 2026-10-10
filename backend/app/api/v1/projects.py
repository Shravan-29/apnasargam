import os
import uuid
import shutil

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.core.security import get_current_user
from app.generation.similarity import extract_feature_vector, cosine_similarity

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])

MIDI_DIR = "generated_midi"


@router.post("/", response_model=ProjectResponse)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_project = Project(user_id=current_user.id, **project.model_dump())
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project


@router.get("/", response_model=list[ProjectResponse])
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Project).filter(Project.user_id == current_user.id).all()


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this project")
    return project


@router.get("/{project_id}/similar")
def get_similar_projects(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns up to 5 of the user's other tracks ranked by cosine
    similarity over a small musical feature vector (average pitch,
    pitch range, note density, tempo). Computed on demand rather than
    stored, since a user's library here is small enough that a live
    pairwise comparison is cheap - no vector database needed at this scale.
    """
    target = db.query(Project).filter(Project.id == project_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Project not found")
    if target.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this project")
    if not target.midi_filename:
        return []

    try:
        target_vec = extract_feature_vector(target.midi_filename, target.bpm or 120)
    except Exception:
        return []

    others = db.query(Project).filter(
        Project.user_id == current_user.id,
        Project.id != project_id,
        Project.midi_filename.isnot(None),
    ).all()

    scored = []
    for other in others:
        try:
            other_vec = extract_feature_vector(other.midi_filename, other.bpm or 120)
        except Exception:
            continue
        score = cosine_similarity(target_vec, other_vec)
        scored.append({
            "id": other.id,
            "name": other.name,
            "genre": other.genre,
            "mood": other.mood,
            "bpm": other.bpm,
            "similarity": round(score, 3),
        })

    scored.sort(key=lambda x: x["similarity"], reverse=True)
    return scored[:5]


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    updates: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this project")

    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this project")

    if project.midi_filename:
        old_path = os.path.join(MIDI_DIR, project.midi_filename)
        if os.path.exists(old_path):
            os.remove(old_path)

    db.delete(project)
    db.commit()
    return None


@router.post("/{project_id}/midi", response_model=ProjectResponse)
def upload_edited_midi(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this project")

    os.makedirs(MIDI_DIR, exist_ok=True)
    new_filename = f"{uuid.uuid4()}.mid"
    new_path = os.path.join(MIDI_DIR, new_filename)
    with open(new_path, "wb") as out_file:
        shutil.copyfileobj(file.file, out_file)

    old_filename = project.midi_filename
    project.midi_filename = new_filename
    db.commit()
    db.refresh(project)

    if old_filename:
        old_path = os.path.join(MIDI_DIR, old_filename)
        if os.path.exists(old_path):
            os.remove(old_path)

    return project