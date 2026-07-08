from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class PaymentAllocationCreate(BaseModel):
    project_id: Optional[str] = None
    estimate_id: Optional[str] = None
    amount: float
    note: Optional[str] = None


class PaymentCreate(BaseModel):
    customer_id: str
    project_id: str
    estimate_id: Optional[str] = None
    amount: float
    payment_method: str
    payment_date: date
    status: str = "received"
    note: Optional[str] = None
    allocations: list[PaymentAllocationCreate] = Field(default_factory=list)


class ReverseCreate(BaseModel):
    reason: str


class PaymentAllocationResponse(BaseModel):
    id: str
    company_id: str
    payment_id: str
    project_id: Optional[str]
    estimate_id: Optional[str]
    amount: float
    note: Optional[str]
    archived_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class PaymentResponse(BaseModel):
    id: str
    company_id: str
    customer_id: str
    project_id: str
    estimate_id: Optional[str]
    amount: float
    currency: str
    payment_method: str
    payment_date: date
    status: str
    note: Optional[str]
    created_by_user_id: str
    reversal_reason: Optional[str]
    reversed_at: Optional[datetime]
    reversed_by_user_id: Optional[str]
    archived_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    allocations: list[PaymentAllocationResponse]


class ExpenseCategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None


class ExpenseCategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class ExpenseCategoryResponse(BaseModel):
    id: str
    company_id: str
    name: str
    description: Optional[str]
    archived_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class ExpenseCreate(BaseModel):
    project_id: Optional[str] = None
    category_id: Optional[str] = None
    supplier_id: Optional[str] = None
    material_id: Optional[str] = None
    description: str
    amount: float
    expense_date: date
    payment_method: str
    status: str = "recorded"
    note: Optional[str] = None


class ExpenseResponse(BaseModel):
    id: str
    company_id: str
    project_id: Optional[str]
    category_id: Optional[str]
    supplier_id: Optional[str]
    material_id: Optional[str]
    description: str
    amount: float
    currency: str
    expense_date: date
    payment_method: str
    status: str
    note: Optional[str]
    created_by_user_id: str
    reversal_reason: Optional[str]
    reversed_at: Optional[datetime]
    reversed_by_user_id: Optional[str]
    archived_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class ProjectFinancialSummaryResponse(BaseModel):
    project_id: str
    customer_id: str
    accepted_estimate_total: Optional[float]
    agreed_project_price: Optional[float]
    revenue_basis: str
    total_received_payments: float
    total_pending_payments: float
    total_reversed_payments: float
    outstanding_balance: Optional[float]
    total_recorded_expenses: float
    total_reversed_expenses: float
    estimated_profit: Optional[float]
    payment_status: str
