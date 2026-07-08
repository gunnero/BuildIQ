from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.calculations.base import CalculationExecutionContext
from app.calculations.registry import calculation_engine_registry
from app.models.calculation import (
    CalculationInput,
    CalculationLineItem,
    CalculationOutput,
    CalculationRun,
)
from app.schemas.calculation import CalculationRunCreate
from app.services.customers import not_found
from app.services.measurements import (
    get_active_measurement_set_for_company,
    get_active_room_for_company,
)
from app.services.projects import get_active_project_for_company, get_active_task_for_company

CALCULATION_RUN_STATUSES = {"draft", "completed", "failed", "archived"}


def validation_error(message: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


def validate_calculation_status(value: str) -> str:
    if value not in CALCULATION_RUN_STATUSES:
        raise validation_error("Невалиден статус на пресметка.")
    return value


def require_project_for_link(project_id: Optional[str]) -> None:
    if project_id is None:
        raise validation_error("Проектот е задолжителен за поврзана пресметка.")


def validate_calculation_links(
    db: Session,
    *,
    company_id: str,
    payload: CalculationRunCreate,
) -> None:
    project_id = payload.project_id
    if project_id is not None:
        get_active_project_for_company(db, company_id=company_id, project_id=project_id)

    if payload.project_task_id is not None:
        require_project_for_link(project_id)
        task = get_active_task_for_company(
            db,
            company_id=company_id,
            task_id=payload.project_task_id,
        )
        if task.project_id != project_id:
            raise validation_error("Задачата не припаѓа на избраниот проект.")

    if payload.room_id is not None:
        require_project_for_link(project_id)
        room = get_active_room_for_company(
            db,
            company_id=company_id,
            room_id=payload.room_id,
        )
        if room.project_id != project_id:
            raise validation_error("Просторијата не припаѓа на избраниот проект.")

    if payload.measurement_set_id is not None:
        require_project_for_link(project_id)
        measurement_set = get_active_measurement_set_for_company(
            db,
            company_id=company_id,
            measurement_set_id=payload.measurement_set_id,
        )
        if measurement_set.project_id != project_id:
            raise validation_error("Сетот мерења не припаѓа на избраниот проект.")


def get_calculation_run_for_company(
    db: Session,
    *,
    company_id: str,
    calculation_run_id: str,
) -> CalculationRun:
    calculation_run = (
        db.query(CalculationRun)
        .filter(
            CalculationRun.id == calculation_run_id,
            CalculationRun.company_id == company_id,
        )
        .one_or_none()
    )
    if calculation_run is None:
        raise not_found()
    return calculation_run


def execute_calculation_run(
    db: Session,
    *,
    company_id: str,
    created_by_user_id: str,
    payload: CalculationRunCreate,
) -> CalculationRun:
    engine = calculation_engine_registry.get(payload.engine_type)
    if engine is None:
        raise validation_error("Непознат тип на пресметка.")

    validate_calculation_links(db, company_id=company_id, payload=payload)
    result = engine.execute(
        payload.input_payload,
        context=CalculationExecutionContext(
            db=db,
            company_id=company_id,
            project_id=payload.project_id,
            project_task_id=payload.project_task_id,
            room_id=payload.room_id,
            measurement_set_id=payload.measurement_set_id,
        ),
    )
    validate_calculation_status(result.status)

    calculation_run = CalculationRun(
        company_id=company_id,
        project_id=payload.project_id,
        project_task_id=payload.project_task_id,
        room_id=payload.room_id,
        measurement_set_id=payload.measurement_set_id,
        engine_type=engine.engine_type,
        engine_version=engine.engine_version,
        status=result.status,
        created_by_user_id=created_by_user_id,
    )
    db.add(calculation_run)
    db.flush()

    now = datetime.utcnow()
    db.add(
        CalculationInput(
            company_id=company_id,
            calculation_run_id=calculation_run.id,
            payload=payload.input_payload,
            created_at=now,
        )
    )
    db.add(
        CalculationOutput(
            company_id=company_id,
            calculation_run_id=calculation_run.id,
            payload=result.output_payload,
            created_at=now,
        )
    )
    for index, line_item in enumerate(result.line_items):
        db.add(
            CalculationLineItem(
                company_id=company_id,
                calculation_run_id=calculation_run.id,
                sort_order=index,
                name=line_item.name,
                description=line_item.description,
                unit=line_item.unit,
                quantity=line_item.quantity,
                payload=line_item.payload,
                created_at=now,
            )
        )
    return calculation_run


def archive_calculation_run(calculation_run: CalculationRun) -> CalculationRun:
    calculation_run.status = validate_calculation_status("archived")
    calculation_run.archived_at = datetime.utcnow()
    return calculation_run
