from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class ProjectCreate(BaseModel):
    customer_id: str
    property_id: str
    name: str
    description: Optional[str] = None
    address: Optional[str] = None
    agreed_project_price: Optional[float] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    agreed_project_price: Optional[float] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None


class ProjectStatusUpdate(BaseModel):
    status: str
    note: Optional[str] = None


class ProjectResponse(BaseModel):
    id: str
    company_id: str
    customer_id: str
    property_id: str
    name: str
    description: Optional[str]
    address: Optional[str]
    status: str
    agreed_project_price: Optional[float]
    start_date: Optional[date]
    due_date: Optional[date]
    archived_at: Optional[datetime]


class ProjectStatusHistoryResponse(BaseModel):
    id: str
    company_id: str
    project_id: str
    from_status: Optional[str]
    to_status: str
    note: Optional[str]
    changed_by_user_id: Optional[str]
    created_at: datetime


class ProjectTimelineEventResponse(BaseModel):
    id: str
    company_id: str
    project_id: str
    event_type: str
    message: Optional[str]
    created_by_user_id: Optional[str]
    created_at: datetime


class ProjectTaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    assigned_user_id: Optional[str] = None
    due_date: Optional[date] = None


class ProjectTaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assigned_user_id: Optional[str] = None
    due_date: Optional[date] = None


class ProjectTaskStatusUpdate(BaseModel):
    status: str


class ProjectTaskResponse(BaseModel):
    id: str
    company_id: str
    project_id: str
    title: str
    description: Optional[str]
    status: str
    assigned_user_id: Optional[str]
    due_date: Optional[date]
    completed_at: Optional[datetime]
    archived_at: Optional[datetime]
