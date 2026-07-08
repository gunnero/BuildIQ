from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CustomerCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    note: Optional[str] = None


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    note: Optional[str] = None


class CustomerResponse(BaseModel):
    id: str
    company_id: str
    name: str
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    note: Optional[str]
    status: str
    archived_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class CustomerContactCreate(BaseModel):
    full_name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    note: Optional[str] = None
    is_primary: bool = False


class CustomerContactResponse(BaseModel):
    id: str
    company_id: str
    customer_id: str
    full_name: str
    phone: Optional[str]
    email: Optional[str]
    role: Optional[str]
    note: Optional[str]
    is_primary: bool
    archived_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class PropertyCreate(BaseModel):
    customer_id: str
    name: str
    address: Optional[str] = None
    city: Optional[str] = None
    note: Optional[str] = None


class PropertyUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    note: Optional[str] = None


class PropertyResponse(BaseModel):
    id: str
    company_id: str
    customer_id: str
    name: str
    address: Optional[str]
    city: Optional[str]
    note: Optional[str]
    status: str
    archived_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class PropertyContactCreate(BaseModel):
    full_name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    note: Optional[str] = None
    is_primary: bool = False


class PropertyContactResponse(BaseModel):
    id: str
    company_id: str
    property_id: str
    full_name: str
    phone: Optional[str]
    email: Optional[str]
    role: Optional[str]
    note: Optional[str]
    is_primary: bool
    archived_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class PropertyNoteCreate(BaseModel):
    content: str


class PropertyNoteResponse(BaseModel):
    id: str
    company_id: str
    property_id: str
    content: str
    created_by_user_id: Optional[str]
    archived_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
