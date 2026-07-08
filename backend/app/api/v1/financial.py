from datetime import datetime

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_company, get_current_user
from app.db.session import get_db
from app.models.financial import Expense, ExpenseCategory, Payment, PaymentAllocation
from app.models.identity import Company, User
from app.schemas.financial import (
    ExpenseCategoryCreate,
    ExpenseCategoryResponse,
    ExpenseCategoryUpdate,
    ExpenseCreate,
    ExpenseResponse,
    PaymentCreate,
    PaymentAllocationResponse,
    PaymentResponse,
    ProjectFinancialSummaryResponse,
    ReverseCreate,
)
from app.services.audit import record_audit_log
from app.services.financial import (
    archive_expense,
    archive_payment,
    create_expense_record,
    create_payment_record,
    get_active_expense_for_company,
    get_active_payment_for_company,
    get_expense_category_for_company,
    get_expense_for_company,
    get_payment_for_company,
    project_financial_summary,
    reverse_expense,
    reverse_payment,
)

router = APIRouter()


def allocation_response(allocation: PaymentAllocation) -> PaymentAllocationResponse:
    return PaymentAllocationResponse(
        id=allocation.id,
        company_id=allocation.company_id,
        payment_id=allocation.payment_id,
        project_id=allocation.project_id,
        estimate_id=allocation.estimate_id,
        amount=allocation.amount,
        note=allocation.note,
        archived_at=allocation.archived_at,
        created_at=allocation.created_at,
        updated_at=allocation.updated_at,
    )


def payment_response(payment: Payment) -> PaymentResponse:
    allocations = [
        allocation
        for allocation in sorted(payment.allocations, key=lambda item: item.created_at)
        if allocation.archived_at is None
    ]
    return PaymentResponse(
        id=payment.id,
        company_id=payment.company_id,
        customer_id=payment.customer_id,
        project_id=payment.project_id,
        estimate_id=payment.estimate_id,
        amount=payment.amount,
        currency=payment.currency,
        payment_method=payment.payment_method,
        payment_date=payment.payment_date,
        status=payment.status,
        note=payment.note,
        created_by_user_id=payment.created_by_user_id,
        reversal_reason=payment.reversal_reason,
        reversed_at=payment.reversed_at,
        reversed_by_user_id=payment.reversed_by_user_id,
        archived_at=payment.archived_at,
        created_at=payment.created_at,
        updated_at=payment.updated_at,
        allocations=[allocation_response(allocation) for allocation in allocations],
    )


def expense_category_response(category: ExpenseCategory) -> ExpenseCategoryResponse:
    return ExpenseCategoryResponse(
        id=category.id,
        company_id=category.company_id,
        name=category.name,
        description=category.description,
        archived_at=category.archived_at,
        created_at=category.created_at,
        updated_at=category.updated_at,
    )


def expense_response(expense: Expense) -> ExpenseResponse:
    return ExpenseResponse(
        id=expense.id,
        company_id=expense.company_id,
        project_id=expense.project_id,
        category_id=expense.category_id,
        supplier_id=expense.supplier_id,
        material_id=expense.material_id,
        description=expense.description,
        amount=expense.amount,
        currency=expense.currency,
        expense_date=expense.expense_date,
        payment_method=expense.payment_method,
        status=expense.status,
        note=expense.note,
        created_by_user_id=expense.created_by_user_id,
        reversal_reason=expense.reversal_reason,
        reversed_at=expense.reversed_at,
        reversed_by_user_id=expense.reversed_by_user_id,
        archived_at=expense.archived_at,
        created_at=expense.created_at,
        updated_at=expense.updated_at,
    )


@router.post(
    "/payments",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["payments"],
    summary="Create payment",
)
def create_payment_endpoint(
    payload: PaymentCreate,
    company: Company = Depends(get_current_company),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PaymentResponse:
    payment = create_payment_record(
        db,
        company_id=company.id,
        user_id=current_user.id,
        payload=payload,
    )
    record_audit_log(
        db,
        action="payment.created",
        entity_type="payment",
        entity_id=payment.id,
        company_id=company.id,
        acting_user_id=current_user.id,
        after_snapshot={
            "amount": payment.amount,
            "status": payment.status,
            "project_id": payment.project_id,
        },
    )
    db.commit()
    db.refresh(payment)
    return payment_response(payment)


@router.get(
    "/payments",
    response_model=list[PaymentResponse],
    tags=["payments"],
    summary="List payments",
)
def list_payments(
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> list[PaymentResponse]:
    payments = (
        db.query(Payment)
        .filter(Payment.company_id == company.id, Payment.archived_at.is_(None))
        .order_by(Payment.created_at.asc())
        .all()
    )
    return [payment_response(payment) for payment in payments]


@router.get(
    "/payments/{payment_id}",
    response_model=PaymentResponse,
    tags=["payments"],
    summary="Read payment",
)
def read_payment(
    payment_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> PaymentResponse:
    payment = get_payment_for_company(db, company_id=company.id, payment_id=payment_id)
    return payment_response(payment)


@router.post(
    "/payments/{payment_id}/reverse",
    response_model=PaymentResponse,
    tags=["payments"],
    summary="Reverse payment",
)
def reverse_payment_endpoint(
    payment_id: str,
    payload: ReverseCreate,
    company: Company = Depends(get_current_company),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PaymentResponse:
    payment = get_active_payment_for_company(db, company_id=company.id, payment_id=payment_id)
    before_status = payment.status
    reverse_payment(payment, reason=payload.reason, user_id=current_user.id)
    record_audit_log(
        db,
        action="payment.reversed",
        entity_type="payment",
        entity_id=payment.id,
        company_id=company.id,
        acting_user_id=current_user.id,
        before_snapshot={"status": before_status},
        after_snapshot={"status": payment.status, "reversal_reason": payment.reversal_reason},
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment_response(payment)


@router.post(
    "/payments/{payment_id}/archive",
    response_model=PaymentResponse,
    tags=["payments"],
    summary="Archive payment",
)
def archive_payment_endpoint(
    payment_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> PaymentResponse:
    payment = get_active_payment_for_company(db, company_id=company.id, payment_id=payment_id)
    archive_payment(payment)
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment_response(payment)


@router.get(
    "/projects/{project_id}/financial-summary",
    response_model=ProjectFinancialSummaryResponse,
    tags=["payments"],
    summary="Read project financial summary",
)
def read_project_financial_summary(
    project_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> ProjectFinancialSummaryResponse:
    return ProjectFinancialSummaryResponse(
        **project_financial_summary(db, company_id=company.id, project_id=project_id)
    )


@router.post(
    "/expense-categories",
    response_model=ExpenseCategoryResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["expenses"],
    summary="Create expense category",
)
def create_expense_category(
    payload: ExpenseCategoryCreate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> ExpenseCategoryResponse:
    category = ExpenseCategory(
        company_id=company.id,
        name=payload.name,
        description=payload.description,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return expense_category_response(category)


@router.get(
    "/expense-categories",
    response_model=list[ExpenseCategoryResponse],
    tags=["expenses"],
    summary="List expense categories",
)
def list_expense_categories(
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> list[ExpenseCategoryResponse]:
    categories = (
        db.query(ExpenseCategory)
        .filter(
            ExpenseCategory.company_id == company.id,
            ExpenseCategory.archived_at.is_(None),
        )
        .order_by(ExpenseCategory.created_at.asc())
        .all()
    )
    return [expense_category_response(category) for category in categories]


@router.patch(
    "/expense-categories/{category_id}",
    response_model=ExpenseCategoryResponse,
    tags=["expenses"],
    summary="Update expense category",
)
def update_expense_category(
    category_id: str,
    payload: ExpenseCategoryUpdate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> ExpenseCategoryResponse:
    category = get_expense_category_for_company(
        db,
        company_id=company.id,
        category_id=category_id,
    )
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    db.add(category)
    db.commit()
    db.refresh(category)
    return expense_category_response(category)


@router.post(
    "/expense-categories/{category_id}/archive",
    response_model=ExpenseCategoryResponse,
    tags=["expenses"],
    summary="Archive expense category",
)
def archive_expense_category(
    category_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> ExpenseCategoryResponse:
    category = get_expense_category_for_company(
        db,
        company_id=company.id,
        category_id=category_id,
    )
    category.archived_at = datetime.utcnow()
    db.add(category)
    db.commit()
    db.refresh(category)
    return expense_category_response(category)


@router.post(
    "/expenses",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["expenses"],
    summary="Create expense",
)
def create_expense_endpoint(
    payload: ExpenseCreate,
    company: Company = Depends(get_current_company),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ExpenseResponse:
    expense = create_expense_record(
        db,
        company_id=company.id,
        user_id=current_user.id,
        payload=payload,
    )
    db.commit()
    db.refresh(expense)
    return expense_response(expense)


@router.get(
    "/expenses",
    response_model=list[ExpenseResponse],
    tags=["expenses"],
    summary="List expenses",
)
def list_expenses(
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> list[ExpenseResponse]:
    expenses = (
        db.query(Expense)
        .filter(Expense.company_id == company.id, Expense.archived_at.is_(None))
        .order_by(Expense.created_at.asc())
        .all()
    )
    return [expense_response(expense) for expense in expenses]


@router.get(
    "/expenses/{expense_id}",
    response_model=ExpenseResponse,
    tags=["expenses"],
    summary="Read expense",
)
def read_expense(
    expense_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> ExpenseResponse:
    expense = get_expense_for_company(db, company_id=company.id, expense_id=expense_id)
    return expense_response(expense)


@router.post(
    "/expenses/{expense_id}/reverse",
    response_model=ExpenseResponse,
    tags=["expenses"],
    summary="Reverse expense",
)
def reverse_expense_endpoint(
    expense_id: str,
    payload: ReverseCreate,
    company: Company = Depends(get_current_company),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ExpenseResponse:
    expense = get_active_expense_for_company(db, company_id=company.id, expense_id=expense_id)
    reverse_expense(expense, reason=payload.reason, user_id=current_user.id)
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense_response(expense)


@router.post(
    "/expenses/{expense_id}/archive",
    response_model=ExpenseResponse,
    tags=["expenses"],
    summary="Archive expense",
)
def archive_expense_endpoint(
    expense_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> ExpenseResponse:
    expense = get_active_expense_for_company(db, company_id=company.id, expense_id=expense_id)
    archive_expense(expense)
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense_response(expense)
