from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_company
from app.db.session import get_db
from app.models.identity import Company
from app.models.measurement import Room, RoomOpening
from app.schemas.measurement import (
    RoomCreate,
    RoomOpeningCreate,
    RoomOpeningResponse,
    RoomOpeningUpdate,
    RoomResponse,
    RoomUpdate,
)
from app.services.measurements import (
    archive_opening,
    archive_room,
    ensure_project_task_context,
    get_active_opening_for_company,
    get_active_room_for_company,
    opening_area,
    room_computed_values,
    validate_opening_type,
    validate_room_type,
)
from app.services.projects import get_active_project_for_company

router = APIRouter(tags=["rooms"])


def room_response(room: Room, db: Session) -> RoomResponse:
    computed = room_computed_values(db, room=room)
    return RoomResponse(
        id=room.id,
        company_id=room.company_id,
        project_id=room.project_id,
        project_task_id=room.project_task_id,
        name=room.name,
        room_type=room.room_type,
        floor=room.floor,
        note=room.note,
        length=room.length,
        width=room.width,
        height=room.height,
        archived_at=room.archived_at,
        created_at=room.created_at,
        updated_at=room.updated_at,
        **computed,
    )


def opening_response(opening: RoomOpening) -> RoomOpeningResponse:
    return RoomOpeningResponse(
        id=opening.id,
        company_id=opening.company_id,
        room_id=opening.room_id,
        opening_type=opening.opening_type,
        name=opening.name,
        width=opening.width,
        height=opening.height,
        quantity=opening.quantity,
        opening_area=opening_area(opening),
        note=opening.note,
        archived_at=opening.archived_at,
        created_at=opening.created_at,
        updated_at=opening.updated_at,
    )


@router.post(
    "/projects/{project_id}/rooms",
    response_model=RoomResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_room(
    project_id: str,
    payload: RoomCreate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> RoomResponse:
    ensure_project_task_context(
        db,
        company_id=company.id,
        project_id=project_id,
        project_task_id=payload.project_task_id,
    )
    validate_room_type(payload.room_type)
    room = Room(
        company_id=company.id,
        project_id=project_id,
        project_task_id=payload.project_task_id,
        name=payload.name,
        room_type=payload.room_type,
        floor=payload.floor,
        note=payload.note,
        length=payload.length,
        width=payload.width,
        height=payload.height,
    )
    db.add(room)
    db.commit()
    db.refresh(room)
    return room_response(room, db)


@router.get("/projects/{project_id}/rooms", response_model=list[RoomResponse])
def list_project_rooms(
    project_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> list[RoomResponse]:
    project = get_active_project_for_company(db, company_id=company.id, project_id=project_id)
    rooms = (
        db.query(Room)
        .filter(
            Room.company_id == company.id,
            Room.project_id == project.id,
            Room.archived_at.is_(None),
        )
        .order_by(Room.created_at.asc())
        .all()
    )
    return [room_response(room, db) for room in rooms]


@router.get("/rooms/{room_id}", response_model=RoomResponse)
def read_room(
    room_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> RoomResponse:
    room = get_active_room_for_company(db, company_id=company.id, room_id=room_id)
    return room_response(room, db)


@router.patch("/rooms/{room_id}", response_model=RoomResponse)
def update_room(
    room_id: str,
    payload: RoomUpdate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> RoomResponse:
    room = get_active_room_for_company(db, company_id=company.id, room_id=room_id)
    values = payload.model_dump(exclude_unset=True)
    if "room_type" in values and values["room_type"] is not None:
        validate_room_type(values["room_type"])
    if "project_task_id" in values:
        ensure_project_task_context(
            db,
            company_id=company.id,
            project_id=room.project_id,
            project_task_id=values["project_task_id"],
        )
    for field, value in values.items():
        setattr(room, field, value)
    db.add(room)
    db.commit()
    db.refresh(room)
    return room_response(room, db)


@router.post("/rooms/{room_id}/archive", response_model=RoomResponse)
def archive_room_endpoint(
    room_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> RoomResponse:
    room = get_active_room_for_company(db, company_id=company.id, room_id=room_id)
    archive_room(room)
    db.add(room)
    db.commit()
    db.refresh(room)
    return room_response(room, db)


@router.post(
    "/rooms/{room_id}/openings",
    response_model=RoomOpeningResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_room_opening(
    room_id: str,
    payload: RoomOpeningCreate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> RoomOpeningResponse:
    room = get_active_room_for_company(db, company_id=company.id, room_id=room_id)
    validate_opening_type(payload.opening_type)
    opening = RoomOpening(
        company_id=company.id,
        room_id=room.id,
        opening_type=payload.opening_type,
        name=payload.name,
        width=payload.width,
        height=payload.height,
        quantity=payload.quantity,
        note=payload.note,
    )
    db.add(opening)
    db.commit()
    db.refresh(opening)
    return opening_response(opening)


@router.get("/rooms/{room_id}/openings", response_model=list[RoomOpeningResponse])
def list_room_openings(
    room_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> list[RoomOpeningResponse]:
    room = get_active_room_for_company(db, company_id=company.id, room_id=room_id)
    openings = (
        db.query(RoomOpening)
        .filter(
            RoomOpening.company_id == company.id,
            RoomOpening.room_id == room.id,
            RoomOpening.archived_at.is_(None),
        )
        .order_by(RoomOpening.created_at.asc())
        .all()
    )
    return [opening_response(opening) for opening in openings]


@router.patch("/openings/{opening_id}", response_model=RoomOpeningResponse)
def update_opening(
    opening_id: str,
    payload: RoomOpeningUpdate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> RoomOpeningResponse:
    opening = get_active_opening_for_company(db, company_id=company.id, opening_id=opening_id)
    values = payload.model_dump(exclude_unset=True)
    if "opening_type" in values and values["opening_type"] is not None:
        validate_opening_type(values["opening_type"])
    for field, value in values.items():
        setattr(opening, field, value)
    db.add(opening)
    db.commit()
    db.refresh(opening)
    return opening_response(opening)


@router.post("/openings/{opening_id}/archive", response_model=RoomOpeningResponse)
def archive_opening_endpoint(
    opening_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> RoomOpeningResponse:
    opening = get_active_opening_for_company(db, company_id=company.id, opening_id=opening_id)
    archive_opening(opening)
    db.add(opening)
    db.commit()
    db.refresh(opening)
    return opening_response(opening)
