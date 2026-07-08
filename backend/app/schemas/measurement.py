from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class RoomCreate(BaseModel):
    name: str
    room_type: str = "room"
    project_task_id: Optional[str] = None
    floor: Optional[str] = None
    note: Optional[str] = None
    length: float
    width: float
    height: float


class RoomUpdate(BaseModel):
    name: Optional[str] = None
    room_type: Optional[str] = None
    project_task_id: Optional[str] = None
    floor: Optional[str] = None
    note: Optional[str] = None
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None


class RoomResponse(BaseModel):
    id: str
    company_id: str
    project_id: str
    project_task_id: Optional[str]
    name: str
    room_type: str
    floor: Optional[str]
    note: Optional[str]
    length: float
    width: float
    height: float
    floor_area: float
    ceiling_area: float
    wall_area_gross: float
    openings_area_total: float
    wall_area_net: float
    total_paintable_area: float
    archived_at: Optional[datetime]


class RoomOpeningCreate(BaseModel):
    opening_type: str
    name: str
    width: float
    height: float
    quantity: int = 1
    note: Optional[str] = None


class RoomOpeningUpdate(BaseModel):
    opening_type: Optional[str] = None
    name: Optional[str] = None
    width: Optional[float] = None
    height: Optional[float] = None
    quantity: Optional[int] = None
    note: Optional[str] = None


class RoomOpeningResponse(BaseModel):
    id: str
    company_id: str
    room_id: str
    opening_type: str
    name: str
    width: float
    height: float
    quantity: int
    opening_area: float
    note: Optional[str]
    archived_at: Optional[datetime]


class MeasurementSetCreate(BaseModel):
    name: str
    description: Optional[str] = None
    project_task_id: Optional[str] = None


class MeasurementSetResponse(BaseModel):
    id: str
    company_id: str
    project_id: str
    project_task_id: Optional[str]
    name: str
    description: Optional[str]
    archived_at: Optional[datetime]


class MeasurementItemCreate(BaseModel):
    name: str
    unit: str
    quantity: float
    note: Optional[str] = None


class MeasurementItemUpdate(BaseModel):
    name: Optional[str] = None
    unit: Optional[str] = None
    quantity: Optional[float] = None
    note: Optional[str] = None


class MeasurementItemResponse(BaseModel):
    id: str
    company_id: str
    measurement_set_id: str
    name: str
    unit: str
    quantity: float
    note: Optional[str]
    archived_at: Optional[datetime]
