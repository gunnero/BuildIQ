from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class CalculationRunCreate(BaseModel):
    engine_type: str
    project_id: Optional[str] = None
    project_task_id: Optional[str] = None
    room_id: Optional[str] = None
    measurement_set_id: Optional[str] = None
    input_payload: dict[str, Any]


class CalculationEngineResponse(BaseModel):
    engine_type: str
    engine_version: str
    implemented: bool
    status: str


class CalculationLineItemResponse(BaseModel):
    id: str
    company_id: str
    calculation_run_id: str
    sort_order: int
    name: str
    description: Optional[str]
    unit: Optional[str]
    quantity: Optional[float]
    payload: Optional[dict[str, Any]]


class CalculationRunResponse(BaseModel):
    id: str
    company_id: str
    project_id: Optional[str]
    project_task_id: Optional[str]
    room_id: Optional[str]
    measurement_set_id: Optional[str]
    engine_type: str
    engine_version: str
    status: str
    input_payload: dict[str, Any]
    output_payload: dict[str, Any]
    line_items: list[CalculationLineItemResponse]
    created_by_user_id: str
    created_at: datetime
    archived_at: Optional[datetime]
