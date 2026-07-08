from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_company, get_current_user
from app.db.session import get_db
from app.models.identity import Company, User
from app.models.project import ProjectTask
from app.schemas.project import (
    ProjectTaskResponse,
    ProjectTaskStatusUpdate,
    ProjectTaskUpdate,
)
from app.services.projects import (
    add_project_timeline_event,
    archive_task,
    change_task_status,
    ensure_assignable_user,
    get_active_task_for_company,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


def project_task_response(task: ProjectTask) -> ProjectTaskResponse:
    return ProjectTaskResponse(
        id=task.id,
        company_id=task.company_id,
        project_id=task.project_id,
        title=task.title,
        description=task.description,
        status=task.status,
        assigned_user_id=task.assigned_user_id,
        due_date=task.due_date,
        completed_at=task.completed_at,
        archived_at=task.archived_at,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


@router.get("/{task_id}", response_model=ProjectTaskResponse)
def read_task(
    task_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> ProjectTaskResponse:
    task = get_active_task_for_company(db, company_id=company.id, task_id=task_id)
    return project_task_response(task)


@router.patch("/{task_id}", response_model=ProjectTaskResponse)
def update_task(
    task_id: str,
    payload: ProjectTaskUpdate,
    company: Company = Depends(get_current_company),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectTaskResponse:
    task = get_active_task_for_company(db, company_id=company.id, task_id=task_id)
    values = payload.model_dump(exclude_unset=True)
    ensure_assignable_user(db, company_id=company.id, user_id=values.get("assigned_user_id"))
    for field, value in values.items():
        setattr(task, field, value)
    add_project_timeline_event(
        db,
        project=task.project,
        event_type="task_updated",
        user_id=current_user.id,
        message=task.title,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return project_task_response(task)


@router.post("/{task_id}/archive", response_model=ProjectTaskResponse)
def archive_task_endpoint(
    task_id: str,
    company: Company = Depends(get_current_company),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectTaskResponse:
    task = get_active_task_for_company(db, company_id=company.id, task_id=task_id)
    archive_task(db, task=task, user_id=current_user.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return project_task_response(task)


@router.post("/{task_id}/status", response_model=ProjectTaskResponse)
def update_task_status(
    task_id: str,
    payload: ProjectTaskStatusUpdate,
    company: Company = Depends(get_current_company),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectTaskResponse:
    task = get_active_task_for_company(db, company_id=company.id, task_id=task_id)
    change_task_status(
        db,
        task=task,
        status_value=payload.status,
        user_id=current_user.id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return project_task_response(task)
