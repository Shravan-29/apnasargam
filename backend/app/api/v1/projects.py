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
    """
    Replaces a project's track with an edited MIDI file from the timeline
    editor. This is what makes the cut/trim UI persist rather than being
    a preview that disappears on refresh - the edited file becomes the
    project's track of record, and the previous file is deleted so
    generated_midi/ doesn't accumulate orphaned versions.
    """
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