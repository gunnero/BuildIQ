from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_company, get_current_user
from app.db.session import get_db
from app.models.identity import Company, User
from app.models.project import (
    Project,
    ProjectStatusHistory,
    ProjectTask,
    ProjectTimelineEvent,
)
from app.schemas.project import (
    ProjectCreate,
    ProjectResponse,
    ProjectStatusHistoryResponse,
    ProjectStatusUpdate,
    ProjectTaskCreate,
    ProjectTaskResponse,
    ProjectTimelineEventResponse,
    ProjectUpdate,
)
from app.services.audit import record_audit_log
from app.services.projects import (
    add_project_timeline_event,
    archive_project,
    ensure_assignable_user,
    ensure_project_customer_property,
    get_active_project_for_company,
    change_project_status,
    get_project_for_company,
)

router = APIRouter(prefix="/projects", tags=["projects"])


def project_response(project: Project) -> ProjectResponse:
    return ProjectResponse(
        id=project.id,
        company_id=project.company_id,
        customer_id=project.customer_id,
        property_id=project.property_id,
        name=project.name,
        description=project.description,
        address=project.address,
        status=project.status,
        agreed_project_price=project.agreed_project_price,
        start_date=project.start_date,
        due_date=project.due_date,
        archived_at=project.archived_at,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


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


def status_history_response(history: ProjectStatusHistory) -> ProjectStatusHistoryResponse:
    return ProjectStatusHistoryResponse(
        id=history.id,
        company_id=history.company_id,
        project_id=history.project_id,
        from_status=history.from_status,
        to_status=history.to_status,
        note=history.note,
        changed_by_user_id=history.changed_by_user_id,
        created_at=history.created_at,
    )


def timeline_event_response(event: ProjectTimelineEvent) -> ProjectTimelineEventResponse:
    return ProjectTimelineEventResponse(
        id=event.id,
        company_id=event.company_id,
        project_id=event.project_id,
        event_type=event.event_type,
        message=event.message,
        created_by_user_id=event.created_by_user_id,
        created_at=event.created_at,
    )


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    company: Company = Depends(get_current_company),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectResponse:
    ensure_project_customer_property(
        db,
        company_id=company.id,
        customer_id=payload.customer_id,
        property_id=payload.property_id,
    )
    project = Project(
        company_id=company.id,
        customer_id=payload.customer_id,
        property_id=payload.property_id,
        name=payload.name,
        description=payload.description,
        address=payload.address,
        agreed_project_price=payload.agreed_project_price,
        start_date=payload.start_date,
        due_date=payload.due_date,
    )
    db.add(project)
    db.flush()
    add_project_timeline_event(
        db,
        project=project,
        event_type="created",
        user_id=current_user.id,
    )
    record_audit_log(
        db,
        action="project.created",
        entity_type="project",
        entity_id=project.id,
        company_id=company.id,
        acting_user_id=current_user.id,
        after_snapshot={"name": project.name, "status": project.status},
    )
    db.commit()
    db.refresh(project)
    return project_response(project)


@router.get("", response_model=list[ProjectResponse])
def list_projects(
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> list[ProjectResponse]:
    projects = (
        db.query(Project)
        .filter(Project.company_id == company.id, Project.archived_at.is_(None))
        .order_by(Project.created_at.asc())
        .all()
    )
    return [project_response(project) for project in projects]


@router.get("/{project_id}", response_model=ProjectResponse)
def read_project(
    project_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> ProjectResponse:
    project = get_active_project_for_company(db, company_id=company.id, project_id=project_id)
    return project_response(project)


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: str,
    payload: ProjectUpdate,
    company: Company = Depends(get_current_company),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectResponse:
    project = get_active_project_for_company(db, company_id=company.id, project_id=project_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    add_project_timeline_event(
        db,
        project=project,
        event_type="updated",
        user_id=current_user.id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project_response(project)


@router.post("/{project_id}/archive", response_model=ProjectResponse)
def archive_project_endpoint(
    project_id: str,
    company: Company = Depends(get_current_company),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectResponse:
    project = get_active_project_for_company(db, company_id=company.id, project_id=project_id)
    archive_project(db, project=project, user_id=current_user.id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project_response(project)


@router.post("/{project_id}/status", response_model=ProjectResponse)
def update_project_status(
    project_id: str,
    payload: ProjectStatusUpdate,
    company: Company = Depends(get_current_company),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectResponse:
    project = get_active_project_for_company(db, company_id=company.id, project_id=project_id)
    change_project_status(
        db,
        project=project,
        status_value=payload.status,
        user_id=current_user.id,
        note=payload.note,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project_response(project)


@router.get("/{project_id}/status-history", response_model=list[ProjectStatusHistoryResponse])
def list_project_status_history(
    project_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> list[ProjectStatusHistoryResponse]:
    project = get_project_for_company(db, company_id=company.id, project_id=project_id)
    history = (
        db.query(ProjectStatusHistory)
        .filter(
            ProjectStatusHistory.company_id == company.id,
            ProjectStatusHistory.project_id == project.id,
        )
        .order_by(ProjectStatusHistory.created_at.asc())
        .all()
    )
    return [status_history_response(item) for item in history]


@router.get("/{project_id}/timeline", response_model=list[ProjectTimelineEventResponse])
def list_project_timeline(
    project_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> list[ProjectTimelineEventResponse]:
    project = get_project_for_company(db, company_id=company.id, project_id=project_id)
    events = (
        db.query(ProjectTimelineEvent)
        .filter(
            ProjectTimelineEvent.company_id == company.id,
            ProjectTimelineEvent.project_id == project.id,
        )
        .order_by(ProjectTimelineEvent.created_at.asc())
        .all()
    )
    return [timeline_event_response(event) for event in events]


@router.post(
    "/{project_id}/tasks",
    response_model=ProjectTaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project_task(
    project_id: str,
    payload: ProjectTaskCreate,
    company: Company = Depends(get_current_company),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectTaskResponse:
    project = get_active_project_for_company(db, company_id=company.id, project_id=project_id)
    ensure_assignable_user(db, company_id=company.id, user_id=payload.assigned_user_id)
    task = ProjectTask(
        company_id=company.id,
        project_id=project.id,
        title=payload.title,
        description=payload.description,
        assigned_user_id=payload.assigned_user_id,
        due_date=payload.due_date,
    )
    db.add(task)
    db.flush()
    add_project_timeline_event(
        db,
        project=project,
        event_type="task_created",
        user_id=current_user.id,
        message=task.title,
    )
    db.commit()
    db.refresh(task)
    return project_task_response(task)


@router.get("/{project_id}/tasks", response_model=list[ProjectTaskResponse])
def list_project_tasks(
    project_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> list[ProjectTaskResponse]:
    project = get_active_project_for_company(db, company_id=company.id, project_id=project_id)
    tasks = (
        db.query(ProjectTask)
        .filter(
            ProjectTask.company_id == company.id,
            ProjectTask.project_id == project.id,
            ProjectTask.archived_at.is_(None),
        )
        .order_by(ProjectTask.created_at.asc())
        .all()
    )
    return [project_task_response(task) for task in tasks]
