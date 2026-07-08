from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class EstimateCreate(BaseModel):
    project_id: str
    customer_id: Optional[str] = None
    property_id: Optional[str] = None
    title: str
    description: Optional[str] = None


class EstimateFromCalculationCreate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class EstimateUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class EstimateStatusUpdate(BaseModel):
    status: str
    note: Optional[str] = None


class EstimateResponse(BaseModel):
    id: str
    company_id: str
    customer_id: str
    property_id: str
    project_id: str
    estimate_number: Optional[str]
    title: str
    description: Optional[str]
    status: str
    source_calculation_run_id: Optional[str]
    sent_at: Optional[datetime]
    accepted_at: Optional[datetime]
    rejected_at: Optional[datetime]
    archived_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class EstimateRevisionResponse(BaseModel):
    id: str
    company_id: str
    estimate_id: str
    revision_number: int
    status: str
    notes: Optional[str]
    terms: Optional[str]
    source_calculation_run_id: Optional[str]
    subtotal: float
    discount_total: float
    adjustment_total: float
    tax_total: float
    total: float
    sent_at: Optional[datetime]
    accepted_at: Optional[datetime]
    rejected_at: Optional[datetime]
    archived_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class EstimateItemCreate(BaseModel):
    item_type: str
    name: str
    description: Optional[str] = None
    material_id: Optional[str] = None
    quantity: float = 1.0
    unit: Optional[str] = None
    unit_price: float = 0.0


class EstimateItemUpdate(BaseModel):
    item_type: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    material_id: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    unit_price: Optional[float] = None


class EstimateItemResponse(BaseModel):
    id: str
    company_id: str
    estimate_revision_id: str
    item_type: str
    name: str
    description: Optional[str]
    material_id: Optional[str]
    quantity: float
    unit: Optional[str]
    unit_price: float
    total_price: float
    source_calculation_run_id: Optional[str]
    source_calculation_line_item_id: Optional[str]
    sort_order: int
    archived_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
