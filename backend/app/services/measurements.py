from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.measurement import MeasurementItem, MeasurementSet, Room, RoomOpening
from app.models.project import Project
from app.services.customers import not_found
from app.services.projects import get_active_project_for_company, get_active_task_for_company

ROOM_TYPES = {
    "room",
    "bathroom",
    "kitchen",
    "hallway",
    "bedroom",
    "living_room",
    "exterior",
    "other",
}
OPENING_TYPES = {"door", "window", "other"}
MEASUREMENT_UNITS = {"m", "m2", "m3", "piece", "kg", "liter", "bag", "roll", "hour"}


def validation_error(message: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


def validate_room_type(value: str) -> str:
    if value not in ROOM_TYPES:
        raise validation_error("Невалиден тип на просторија.")
    return value


def validate_opening_type(value: str) -> str:
    if value not in OPENING_TYPES:
        raise validation_error("Невалиден тип на отвор.")
    return value


def validate_measurement_unit(value: str) -> str:
    if value not in MEASUREMENT_UNITS:
        raise validation_error("Невалидна мерна единица.")
    return value


def ensure_task_belongs_to_project(
    db: Session,
    *,
    company_id: str,
    project_id: str,
    project_task_id: Optional[str],
) -> None:
    if project_task_id is None:
        return
    task = get_active_task_for_company(
        db,
        company_id=company_id,
        task_id=project_task_id,
    )
    if task.project_id != project_id:
        raise validation_error("Задачата не припаѓа на избраниот проект.")


def get_active_room_for_company(
    db: Session,
    *,
    company_id: str,
    room_id: str,
) -> Room:
    room = (
        db.query(Room)
        .join(Project, Room.project_id == Project.id)
        .filter(
            Room.id == room_id,
            Room.company_id == company_id,
            Room.archived_at.is_(None),
            Project.company_id == company_id,
            Project.archived_at.is_(None),
        )
        .one_or_none()
    )
    if room is None:
        raise not_found()
    return room


def get_active_opening_for_company(
    db: Session,
    *,
    company_id: str,
    opening_id: str,
) -> RoomOpening:
    opening = (
        db.query(RoomOpening)
        .join(Room, RoomOpening.room_id == Room.id)
        .join(Project, Room.project_id == Project.id)
        .filter(
            RoomOpening.id == opening_id,
            RoomOpening.company_id == company_id,
            RoomOpening.archived_at.is_(None),
            Room.company_id == company_id,
            Room.archived_at.is_(None),
            Project.company_id == company_id,
            Project.archived_at.is_(None),
        )
        .one_or_none()
    )
    if opening is None:
        raise not_found()
    return opening


def get_active_measurement_set_for_company(
    db: Session,
    *,
    company_id: str,
    measurement_set_id: str,
) -> MeasurementSet:
    measurement_set = (
        db.query(MeasurementSet)
        .join(Project, MeasurementSet.project_id == Project.id)
        .filter(
            MeasurementSet.id == measurement_set_id,
            MeasurementSet.company_id == company_id,
            MeasurementSet.archived_at.is_(None),
            Project.company_id == company_id,
            Project.archived_at.is_(None),
        )
        .one_or_none()
    )
    if measurement_set is None:
        raise not_found()
    return measurement_set


def get_active_measurement_item_for_company(
    db: Session,
    *,
    company_id: str,
    measurement_item_id: str,
) -> MeasurementItem:
    measurement_item = (
        db.query(MeasurementItem)
        .join(MeasurementSet, MeasurementItem.measurement_set_id == MeasurementSet.id)
        .join(Project, MeasurementSet.project_id == Project.id)
        .filter(
            MeasurementItem.id == measurement_item_id,
            MeasurementItem.company_id == company_id,
            MeasurementItem.archived_at.is_(None),
            MeasurementSet.company_id == company_id,
            MeasurementSet.archived_at.is_(None),
            Project.company_id == company_id,
            Project.archived_at.is_(None),
        )
        .one_or_none()
    )
    if measurement_item is None:
        raise not_found()
    return measurement_item


def ensure_project_task_context(
    db: Session,
    *,
    company_id: str,
    project_id: str,
    project_task_id: Optional[str],
) -> None:
    get_active_project_for_company(db, company_id=company_id, project_id=project_id)
    ensure_task_belongs_to_project(
        db,
        company_id=company_id,
        project_id=project_id,
        project_task_id=project_task_id,
    )


def opening_area(opening: RoomOpening) -> float:
    return round(opening.width * opening.height * opening.quantity, 4)


def room_computed_values(db: Session, *, room: Room) -> dict[str, float]:
    openings = (
        db.query(RoomOpening)
        .filter(
            RoomOpening.company_id == room.company_id,
            RoomOpening.room_id == room.id,
            RoomOpening.archived_at.is_(None),
        )
        .all()
    )
    floor_area = room.length * room.width
    ceiling_area = floor_area
    wall_area_gross = 2 * (room.length + room.width) * room.height
    openings_area_total = sum(opening_area(opening) for opening in openings)
    wall_area_net = wall_area_gross - openings_area_total
    total_paintable_area = ceiling_area + wall_area_net
    return {
        "floor_area": round(floor_area, 4),
        "ceiling_area": round(ceiling_area, 4),
        "wall_area_gross": round(wall_area_gross, 4),
        "openings_area_total": round(openings_area_total, 4),
        "wall_area_net": round(wall_area_net, 4),
        "total_paintable_area": round(total_paintable_area, 4),
    }


def archive_room(room: Room) -> Room:
    room.archived_at = datetime.utcnow()
    return room


def archive_opening(opening: RoomOpening) -> RoomOpening:
    opening.archived_at = datetime.utcnow()
    return opening


def archive_measurement_item(measurement_item: MeasurementItem) -> MeasurementItem:
    measurement_item.archived_at = datetime.utcnow()
    return measurement_item
