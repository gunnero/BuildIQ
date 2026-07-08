from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MaterialCategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None


class MaterialCategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class MaterialCategoryResponse(BaseModel):
    id: str
    company_id: str
    name: str
    description: Optional[str]
    archived_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class MaterialManufacturerCreate(BaseModel):
    name: str
    website: Optional[str] = None
    note: Optional[str] = None


class MaterialManufacturerUpdate(BaseModel):
    name: Optional[str] = None
    website: Optional[str] = None
    note: Optional[str] = None


class MaterialManufacturerResponse(BaseModel):
    id: str
    company_id: str
    name: str
    website: Optional[str]
    note: Optional[str]
    archived_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class MaterialUnitCreate(BaseModel):
    key: str
    name: str
    description: Optional[str] = None


class MaterialUnitResponse(BaseModel):
    id: str
    company_id: Optional[str]
    key: str
    name: str
    description: Optional[str]
    is_default: bool
    archived_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class MaterialCreate(BaseModel):
    name: str
    sku: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[str] = None
    manufacturer_id: Optional[str] = None
    unit_id: str
    coverage_value: Optional[float] = None
    coverage_unit: Optional[str] = None
    package_quantity: Optional[float] = None
    waste_percentage_default: Optional[float] = None
    is_active: bool = True


class MaterialUpdate(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[str] = None
    manufacturer_id: Optional[str] = None
    unit_id: Optional[str] = None
    coverage_value: Optional[float] = None
    coverage_unit: Optional[str] = None
    package_quantity: Optional[float] = None
    waste_percentage_default: Optional[float] = None
    is_active: Optional[bool] = None


class MaterialResponse(BaseModel):
    id: str
    company_id: str
    name: str
    sku: Optional[str]
    description: Optional[str]
    category_id: Optional[str]
    manufacturer_id: Optional[str]
    unit_id: str
    coverage_value: Optional[float]
    coverage_unit: Optional[str]
    package_quantity: Optional[float]
    waste_percentage_default: Optional[float]
    is_active: bool
    archived_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class MaterialConsumptionRuleCreate(BaseModel):
    material_id: str
    engine_type: str
    name: str
    input_unit: Optional[str] = None
    consumption_rate: Optional[float] = None
    waste_percentage: Optional[float] = None
    description: Optional[str] = None


class MaterialConsumptionRuleUpdate(BaseModel):
    material_id: Optional[str] = None
    engine_type: Optional[str] = None
    name: Optional[str] = None
    input_unit: Optional[str] = None
    consumption_rate: Optional[float] = None
    waste_percentage: Optional[float] = None
    description: Optional[str] = None


class MaterialConsumptionRuleResponse(BaseModel):
    id: str
    company_id: str
    material_id: str
    engine_type: str
    name: str
    input_unit: Optional[str]
    consumption_rate: Optional[float]
    waste_percentage: Optional[float]
    description: Optional[str]
    archived_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
