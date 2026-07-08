from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.identity import User
from app.models.project import (
    Project,
    ProjectStatusHistory,
    ProjectTask,
    ProjectTimelineEvent,
)
from app.services.customers import (
    get_active_customer_for_company,
    get_active_property_for_company,
    not_found,
)

PROJECT_STATUSES = {
    "draft",
    "planned",
    "active",
    "paused",
    "completed",
    "archived",
    "cancelled",
}
TASK_STATUSES = {
    "draft",
    "pending",
    "active",
    "completed",
    "cancelled",
    "archived",
}


def validation_error(message: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


def validate_project_status(value: str, *, allow_archived: bool = False) -> str:
    if value not in PROJECT_STATUSES:
        raise validation_error("Невалиден статус на проект.")
    if value == "archived" and not allow_archived:
        raise validation_error("Користете ја архивската постапка за архивирање проект.")
    return value


def validate_task_status(value: str, *, allow_archived: bool = False) -> str:
    if value not in TASK_STATUSES:
        raise validation_error("Невалиден статус на задача.")
    if value == "archived" and not allow_archived:
        raise validation_error("Користете ја архивската постапка за архивирање задача.")
    return value


def get_active_project_for_company(
    db: Session,
    *,
    company_id: str,
    project_id: str,
) -> Project:
    project = (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.company_id == company_id,
            Project.archived_at.is_(None),
        )
        .one_or_none()
    )
    if project is None:
        raise not_found()
    return project


def get_project_for_company(
    db: Session,
    *,
    company_id: str,
    project_id: str,
) -> Project:
    project = (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.company_id == company_id,
        )
        .one_or_none()
    )
    if project is None:
        raise not_found()
    return project


def get_active_task_for_company(
    db: Session,
    *,
    company_id: str,
    task_id: str,
) -> ProjectTask:
    task = (
        db.query(ProjectTask)
        .join(Project, ProjectTask.project_id == Project.id)
        .filter(
            ProjectTask.id == task_id,
            ProjectTask.company_id == company_id,
            ProjectTask.archived_at.is_(None),
            Project.company_id == company_id,
            Project.archived_at.is_(None),
        )
        .one_or_none()
    )
    if task is None:
        raise not_found()
    return task


def ensure_project_customer_property(
    db: Session,
    *,
    company_id: str,
    customer_id: str,
    property_id: str,
) -> None:
    customer = get_active_customer_for_company(
        db,
        company_id=company_id,
        customer_id=customer_id,
    )
    property_item = get_active_property_for_company(
        db,
        company_id=company_id,
        property_id=property_id,
    )
    if property_item.customer_id != customer.id:
        raise validation_error("Имотот не припаѓа на избраниот клиент.")


def ensure_assignable_user(
    db: Session,
    *,
    company_id: str,
    user_id: Optional[str],
) -> None:
    if user_id is None:
        return
    user = (
        db.query(User)
        .filter(User.id == user_id, User.company_id == company_id, User.status == "active")
        .one_or_none()
    )
    if user is None:
        raise validation_error("Избраниот корисник не е достапен.")


def add_project_timeline_event(
    db: Session,
    *,
    project: Project,
    event_type: str,
    user_id: Optional[str],
    message: Optional[str] = None,
) -> ProjectTimelineEvent:
    event = ProjectTimelineEvent(
        company_id=project.company_id,
        project_id=project.id,
        event_type=event_type,
        message=message,
        created_by_user_id=user_id,
        created_at=datetime.utcnow(),
    )
    db.add(event)
    return event


def add_project_status_history(
    db: Session,
    *,
    project: Project,
    from_status: Optional[str],
    to_status: str,
    user_id: Optional[str],
    note: Optional[str] = None,
) -> ProjectStatusHistory:
    history = ProjectStatusHistory(
        company_id=project.company_id,
        project_id=project.id,
        from_status=from_status,
        to_status=to_status,
        note=note,
        changed_by_user_id=user_id,
        created_at=datetime.utcnow(),
    )
    db.add(history)
    return history


def change_project_status(
    db: Session,
    *,
    project: Project,
    status_value: str,
    user_id: Optional[str],
    note: Optional[str] = None,
) -> Project:
    to_status = validate_project_status(status_value)
    from_status = project.status
    project.status = to_status
    add_project_status_history(
        db,
        project=project,
        from_status=from_status,
        to_status=to_status,
        user_id=user_id,
        note=note,
    )
    add_project_timeline_event(
        db,
        project=project,
        event_type="status_changed",
        user_id=user_id,
        message=note,
    )
    return project


def archive_project(db: Session, *, project: Project, user_id: Optional[str]) -> Project:
    from_status = project.status
    project.status = validate_project_status("archived", allow_archived=True)
    project.archived_at = datetime.utcnow()
    add_project_status_history(
        db,
        project=project,
        from_status=from_status,
        to_status=project.status,
        user_id=user_id,
        note="Archived",
    )
    add_project_timeline_event(
        db,
        project=project,
        event_type="archived",
        user_id=user_id,
        message="Archived",
    )
    return project


def change_task_status(
    db: Session,
    *,
    task: ProjectTask,
    status_value: str,
    user_id: Optional[str],
) -> ProjectTask:
    task.status = validate_task_status(status_value)
    task.completed_at = datetime.utcnow() if task.status == "completed" else None
    add_project_timeline_event(
        db,
        project=task.project,
        event_type="task_status_changed",
        user_id=user_id,
        message=task.title,
    )
    return task


def archive_task(db: Session, *, task: ProjectTask, user_id: Optional[str]) -> ProjectTask:
    task.status = validate_task_status("archived", allow_archived=True)
    task.archived_at = datetime.utcnow()
    add_project_timeline_event(
        db,
        project=task.project,
        event_type="task_archived",
        user_id=user_id,
        message=task.title,
    )
    return task
