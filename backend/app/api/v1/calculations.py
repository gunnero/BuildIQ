from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_company, get_current_user
from app.calculations.registry import calculation_engine_registry
from app.db.session import get_db
from app.models.calculation import CalculationLineItem, CalculationRun
from app.models.identity import Company, User
from app.schemas.calculation import (
    CalculationEngineResponse,
    CalculationLineItemResponse,
    CalculationRunCreate,
    CalculationRunResponse,
)
from app.services.calculations import (
    archive_calculation_run,
    execute_calculation_run,
    get_calculation_run_for_company,
)

router = APIRouter(tags=["calculations"])


def calculation_line_item_response(line_item: CalculationLineItem) -> CalculationLineItemResponse:
    return CalculationLineItemResponse(
        id=line_item.id,
        company_id=line_item.company_id,
        calculation_run_id=line_item.calculation_run_id,
        sort_order=line_item.sort_order,
        name=line_item.name,
        description=line_item.description,
        unit=line_item.unit,
        quantity=line_item.quantity,
        payload=line_item.payload,
    )


def calculation_run_response(calculation_run: CalculationRun) -> CalculationRunResponse:
    input_payload = calculation_run.input.payload if calculation_run.input is not None else {}
    output_payload = calculation_run.output.payload if calculation_run.output is not None else {}
    return CalculationRunResponse(
        id=calculation_run.id,
        company_id=calculation_run.company_id,
        project_id=calculation_run.project_id,
        project_task_id=calculation_run.project_task_id,
        room_id=calculation_run.room_id,
        measurement_set_id=calculation_run.measurement_set_id,
        engine_type=calculation_run.engine_type,
        engine_version=calculation_run.engine_version,
        status=calculation_run.status,
        input_payload=input_payload,
        output_payload=output_payload,
        line_items=[
            calculation_line_item_response(line_item)
            for line_item in sorted(calculation_run.line_items, key=lambda item: item.sort_order)
        ],
        created_by_user_id=calculation_run.created_by_user_id,
        created_at=calculation_run.created_at,
        archived_at=calculation_run.archived_at,
    )


@router.get("/calculation-engines", response_model=list[CalculationEngineResponse])
def list_calculation_engines(
    company: Company = Depends(get_current_company),
) -> list[CalculationEngineResponse]:
    _ = company
    return [
        CalculationEngineResponse(**engine.metadata())
        for engine in calculation_engine_registry.list()
    ]


@router.post(
    "/calculations/run",
    response_model=CalculationRunResponse,
    status_code=status.HTTP_201_CREATED,
)
def run_calculation(
    payload: CalculationRunCreate,
    company: Company = Depends(get_current_company),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CalculationRunResponse:
    calculation_run = execute_calculation_run(
        db,
        company_id=company.id,
        created_by_user_id=current_user.id,
        payload=payload,
    )
    db.commit()
    db.refresh(calculation_run)
    return calculation_run_response(calculation_run)


@router.get("/calculations", response_model=list[CalculationRunResponse])
def list_calculations(
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> list[CalculationRunResponse]:
    calculation_runs = (
        db.query(CalculationRun)
        .filter(
            CalculationRun.company_id == company.id,
            CalculationRun.status != "archived",
        )
        .order_by(CalculationRun.created_at.asc())
        .all()
    )
    return [calculation_run_response(calculation_run) for calculation_run in calculation_runs]


@router.get("/calculations/{calculation_run_id}", response_model=CalculationRunResponse)
def read_calculation(
    calculation_run_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> CalculationRunResponse:
    calculation_run = get_calculation_run_for_company(
        db,
        company_id=company.id,
        calculation_run_id=calculation_run_id,
    )
    return calculation_run_response(calculation_run)


@router.post("/calculations/{calculation_run_id}/archive", response_model=CalculationRunResponse)
def archive_calculation(
    calculation_run_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> CalculationRunResponse:
    calculation_run = get_calculation_run_for_company(
        db,
        company_id=company.id,
        calculation_run_id=calculation_run_id,
    )
    archive_calculation_run(calculation_run)
    db.add(calculation_run)
    db.commit()
    db.refresh(calculation_run)
    return calculation_run_response(calculation_run)
