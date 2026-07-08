from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_company
from app.db.session import get_db
from app.models.identity import Company
from app.models.measurement import MeasurementItem, MeasurementSet
from app.schemas.measurement import (
    MeasurementItemCreate,
    MeasurementItemResponse,
    MeasurementItemUpdate,
    MeasurementSetCreate,
    MeasurementSetResponse,
)
from app.services.measurements import (
    archive_measurement_item,
    ensure_project_task_context,
    get_active_measurement_item_for_company,
    get_active_measurement_set_for_company,
    validate_measurement_unit,
)
from app.services.projects import get_active_project_for_company

router = APIRouter(tags=["measurements"])


def measurement_set_response(measurement_set: MeasurementSet) -> MeasurementSetResponse:
    return MeasurementSetResponse(
        id=measurement_set.id,
        company_id=measurement_set.company_id,
        project_id=measurement_set.project_id,
        project_task_id=measurement_set.project_task_id,
        name=measurement_set.name,
        description=measurement_set.description,
        archived_at=measurement_set.archived_at,
        created_at=measurement_set.created_at,
        updated_at=measurement_set.updated_at,
    )


def measurement_item_response(measurement_item: MeasurementItem) -> MeasurementItemResponse:
    return MeasurementItemResponse(
        id=measurement_item.id,
        company_id=measurement_item.company_id,
        measurement_set_id=measurement_item.measurement_set_id,
        name=measurement_item.name,
        unit=measurement_item.unit,
        quantity=measurement_item.quantity,
        note=measurement_item.note,
        archived_at=measurement_item.archived_at,
        created_at=measurement_item.created_at,
        updated_at=measurement_item.updated_at,
    )


@router.post(
    "/projects/{project_id}/measurement-sets",
    response_model=MeasurementSetResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_measurement_set(
    project_id: str,
    payload: MeasurementSetCreate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> MeasurementSetResponse:
    ensure_project_task_context(
        db,
        company_id=company.id,
        project_id=project_id,
        project_task_id=payload.project_task_id,
    )
    measurement_set = MeasurementSet(
        company_id=company.id,
        project_id=project_id,
        project_task_id=payload.project_task_id,
        name=payload.name,
        description=payload.description,
    )
    db.add(measurement_set)
    db.commit()
    db.refresh(measurement_set)
    return measurement_set_response(measurement_set)


@router.get("/projects/{project_id}/measurement-sets", response_model=list[MeasurementSetResponse])
def list_project_measurement_sets(
    project_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> list[MeasurementSetResponse]:
    project = get_active_project_for_company(db, company_id=company.id, project_id=project_id)
    measurement_sets = (
        db.query(MeasurementSet)
        .filter(
            MeasurementSet.company_id == company.id,
            MeasurementSet.project_id == project.id,
            MeasurementSet.archived_at.is_(None),
        )
        .order_by(MeasurementSet.created_at.asc())
        .all()
    )
    return [measurement_set_response(measurement_set) for measurement_set in measurement_sets]


@router.get("/measurement-sets/{measurement_set_id}", response_model=MeasurementSetResponse)
def read_measurement_set(
    measurement_set_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> MeasurementSetResponse:
    measurement_set = get_active_measurement_set_for_company(
        db,
        company_id=company.id,
        measurement_set_id=measurement_set_id,
    )
    return measurement_set_response(measurement_set)


@router.post(
    "/measurement-sets/{measurement_set_id}/items",
    response_model=MeasurementItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_measurement_item(
    measurement_set_id: str,
    payload: MeasurementItemCreate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> MeasurementItemResponse:
    measurement_set = get_active_measurement_set_for_company(
        db,
        company_id=company.id,
        measurement_set_id=measurement_set_id,
    )
    validate_measurement_unit(payload.unit)
    measurement_item = MeasurementItem(
        company_id=company.id,
        measurement_set_id=measurement_set.id,
        name=payload.name,
        unit=payload.unit,
        quantity=payload.quantity,
        note=payload.note,
    )
    db.add(measurement_item)
    db.commit()
    db.refresh(measurement_item)
    return measurement_item_response(measurement_item)


@router.get("/measurement-sets/{measurement_set_id}/items", response_model=list[MeasurementItemResponse])
def list_measurement_items(
    measurement_set_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> list[MeasurementItemResponse]:
    measurement_set = get_active_measurement_set_for_company(
        db,
        company_id=company.id,
        measurement_set_id=measurement_set_id,
    )
    measurement_items = (
        db.query(MeasurementItem)
        .filter(
            MeasurementItem.company_id == company.id,
            MeasurementItem.measurement_set_id == measurement_set.id,
            MeasurementItem.archived_at.is_(None),
        )
        .order_by(MeasurementItem.created_at.asc())
        .all()
    )
    return [measurement_item_response(measurement_item) for measurement_item in measurement_items]


@router.patch("/measurement-items/{measurement_item_id}", response_model=MeasurementItemResponse)
def update_measurement_item(
    measurement_item_id: str,
    payload: MeasurementItemUpdate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> MeasurementItemResponse:
    measurement_item = get_active_measurement_item_for_company(
        db,
        company_id=company.id,
        measurement_item_id=measurement_item_id,
    )
    values = payload.model_dump(exclude_unset=True)
    if "unit" in values and values["unit"] is not None:
        validate_measurement_unit(values["unit"])
    for field, value in values.items():
        setattr(measurement_item, field, value)
    db.add(measurement_item)
    db.commit()
    db.refresh(measurement_item)
    return measurement_item_response(measurement_item)


@router.post("/measurement-items/{measurement_item_id}/archive", response_model=MeasurementItemResponse)
def archive_measurement_item_endpoint(
    measurement_item_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> MeasurementItemResponse:
    measurement_item = get_active_measurement_item_for_company(
        db,
        company_id=company.id,
        measurement_item_id=measurement_item_id,
    )
    archive_measurement_item(measurement_item)
    db.add(measurement_item)
    db.commit()
    db.refresh(measurement_item)
    return measurement_item_response(measurement_item)
