from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class SupplierCreate(BaseModel):
    name: str
    supplier_type: str = "supplier"
    parent_supplier_id: Optional[str] = None
    tax_number: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    note: Optional[str] = None


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    supplier_type: Optional[str] = None
    parent_supplier_id: Optional[str] = None
    tax_number: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    note: Optional[str] = None
    status: Optional[str] = None


class SupplierResponse(BaseModel):
    id: str
    company_id: str
    parent_supplier_id: Optional[str]
    name: str
    supplier_type: str
    tax_number: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    note: Optional[str]
    status: str
    archived_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class SupplierContactCreate(BaseModel):
    full_name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    note: Optional[str] = None
    is_primary: bool = False


class SupplierContactUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    note: Optional[str] = None
    is_primary: Optional[bool] = None


class SupplierContactResponse(BaseModel):
    id: str
    company_id: str
    supplier_id: str
    full_name: str
    phone: Optional[str]
    email: Optional[str]
    role: Optional[str]
    note: Optional[str]
    is_primary: bool
    archived_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class SupplierAgreementCreate(BaseModel):
    agreement_number: str
    status: str = "draft"
    starts_on: Optional[date] = None
    ends_on: Optional[date] = None
    terms_snapshot: dict[str, Any] = Field(default_factory=dict)
    notes: Optional[str] = None


class SupplierAgreementUpdate(BaseModel):
    agreement_number: Optional[str] = None
    status: Optional[str] = None
    starts_on: Optional[date] = None
    ends_on: Optional[date] = None
    terms_snapshot: Optional[dict[str, Any]] = None
    notes: Optional[str] = None


class SupplierAgreementResponse(BaseModel):
    id: str
    company_id: str
    supplier_id: str
    agreement_number: str
    status: str
    starts_on: Optional[date]
    ends_on: Optional[date]
    terms_snapshot: dict[str, Any]
    notes: Optional[str]
    archived_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class PriceBookCreate(BaseModel):
    supplier_id: Optional[str] = None
    supplier_agreement_id: Optional[str] = None
    name: str
    price_type: str
    status: str = "active"
    currency: str = "MKD"
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    notes: Optional[str] = None


class PriceBookUpdate(BaseModel):
    supplier_id: Optional[str] = None
    supplier_agreement_id: Optional[str] = None
    name: Optional[str] = None
    price_type: Optional[str] = None
    status: Optional[str] = None
    currency: Optional[str] = None
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    notes: Optional[str] = None


class PriceBookResponse(BaseModel):
    id: str
    company_id: str
    supplier_id: Optional[str]
    supplier_agreement_id: Optional[str]
    name: str
    price_type: str
    status: str
    currency: str
    valid_from: date
    valid_until: Optional[date]
    notes: Optional[str]
    archived_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class PriceBookItemCreate(BaseModel):
    material_id: str
    supplier_id: Optional[str] = None
    supplier_sku: Optional[str] = None
    unit_price: float
    currency: str = "MKD"
    valid_from: date
    valid_until: Optional[date] = None
    notes: Optional[str] = None


class PriceBookItemUpdate(BaseModel):
    material_id: Optional[str] = None
    supplier_id: Optional[str] = None
    supplier_sku: Optional[str] = None
    unit_price: Optional[float] = None
    currency: Optional[str] = None
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    notes: Optional[str] = None


class PriceBookItemResponse(BaseModel):
    id: str
    company_id: str
    price_book_id: str
    material_id: str
    supplier_id: Optional[str]
    supplier_sku: Optional[str]
    unit_price: float
    currency: str
    valid_from: date
    valid_until: Optional[date]
    notes: Optional[str]
    archived_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class ProjectMaterialPriceOverrideCreate(BaseModel):
    material_id: str
    supplier_id: Optional[str] = None
    unit_price: float
    currency: str = "MKD"
    valid_from: date
    valid_until: Optional[date] = None
    reason: Optional[str] = None
    notes: Optional[str] = None


class ProjectMaterialPriceOverrideUpdate(BaseModel):
    material_id: Optional[str] = None
    supplier_id: Optional[str] = None
    unit_price: Optional[float] = None
    currency: Optional[str] = None
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    reason: Optional[str] = None
    notes: Optional[str] = None


class ProjectMaterialPriceOverrideResponse(BaseModel):
    id: str
    company_id: str
    project_id: str
    material_id: str
    supplier_id: Optional[str]
    unit_price: float
    currency: str
    valid_from: date
    valid_until: Optional[date]
    reason: Optional[str]
    notes: Optional[str]
    created_by_user_id: str
    archived_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class ResolvedPriceResponse(BaseModel):
    material_id: str
    supplier_id: Optional[str]
    resolved_price: Optional[float]
    currency: Optional[str]
    source_type: str
    source_id: Optional[str]
    valid_from: Optional[date]
    valid_until: Optional[date]
    notes: Optional[str]
