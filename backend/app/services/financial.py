from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.estimate import Estimate, EstimateRevision
from app.models.financial import Expense, ExpenseCategory, Payment, PaymentAllocation
from app.models.material import Material
from app.models.procurement import Supplier
from app.models.project import Project
from app.schemas.financial import ExpenseCreate, PaymentAllocationCreate, PaymentCreate
from app.services.customers import not_found
from app.services.estimates import calculate_revision_totals, get_active_estimate_for_company
from app.services.projects import get_active_project_for_company

PAYMENT_METHODS = {"cash", "bank_transfer", "card", "other"}
PAYMENT_STATUSES = {"received", "pending", "reversed", "archived"}
EXPENSE_STATUSES = {"recorded", "reimbursed", "reversed", "archived"}


def validation_error(message: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


def validate_positive_amount(value: float, *, message: str) -> float:
    if value <= 0:
        raise validation_error(message)
    return value


def validate_payment_method(value: str) -> str:
    if value not in PAYMENT_METHODS:
        raise validation_error("Невалиден начин на плаќање.")
    return value


def validate_payment_status(value: str, *, allow_archived: bool = False) -> str:
    if value not in PAYMENT_STATUSES:
        raise validation_error("Невалиден статус на уплата.")
    if value == "archived" and not allow_archived:
        raise validation_error("Користете ја архивската постапка за архивирање уплата.")
    return value


def validate_expense_status(value: str, *, allow_archived: bool = False) -> str:
    if value not in EXPENSE_STATUSES:
        raise validation_error("Невалиден статус на трошок.")
    if value == "archived" and not allow_archived:
        raise validation_error("Користете ја архивската постапка за архивирање трошок.")
    return value


def get_customer_for_payment(db: Session, *, company_id: str, customer_id: str) -> Customer:
    customer = (
        db.query(Customer)
        .filter(
            Customer.id == customer_id,
            Customer.company_id == company_id,
            Customer.archived_at.is_(None),
        )
        .one_or_none()
    )
    if customer is None:
        raise validation_error("Клиентот не е достапен за оваа компанија.")
    return customer


def validate_payment_links(
    db: Session,
    *,
    company_id: str,
    payload: PaymentCreate,
) -> tuple[Customer, Project, Optional[Estimate]]:
    customer = get_customer_for_payment(db, company_id=company_id, customer_id=payload.customer_id)
    project = get_active_project_for_company(
        db,
        company_id=company_id,
        project_id=payload.project_id,
    )
    if project.customer_id != customer.id:
        raise validation_error("Уплатата не одговара на клиентот на проектот.")

    estimate = None
    if payload.estimate_id is not None:
        estimate = get_active_estimate_for_company(
            db,
            company_id=company_id,
            estimate_id=payload.estimate_id,
        )
        if estimate.project_id != project.id or estimate.customer_id != customer.id:
            raise validation_error("Понудата не одговара на избраниот проект и клиент.")

    return customer, project, estimate


def validate_payment_allocation(
    db: Session,
    *,
    company_id: str,
    payment_project_id: str,
    payload: PaymentAllocationCreate,
) -> PaymentAllocationCreate:
    amount = validate_positive_amount(
        payload.amount,
        message="Износот на алокацијата мора да биде позитивен.",
    )
    project_id = payload.project_id
    estimate_id = payload.estimate_id
    if project_id is None and estimate_id is None:
        raise validation_error("Алокацијата мора да има проект или понуда.")

    if project_id is not None:
        project = get_active_project_for_company(
            db,
            company_id=company_id,
            project_id=project_id,
        )
        if project.id != payment_project_id:
            raise validation_error("Алокацијата мора да припаѓа на проектот на уплатата.")

    if estimate_id is not None:
        estimate = get_active_estimate_for_company(
            db,
            company_id=company_id,
            estimate_id=estimate_id,
        )
        if estimate.project_id != payment_project_id:
            raise validation_error("Алокацијата кон понуда мора да припаѓа на проектот на уплатата.")
        if project_id is None:
            project_id = estimate.project_id

    return PaymentAllocationCreate(
        project_id=project_id,
        estimate_id=estimate_id,
        amount=amount,
        note=payload.note,
    )


def payment_allocations_for_payload(payload: PaymentCreate) -> list[PaymentAllocationCreate]:
    if payload.allocations:
        return payload.allocations
    return [
        PaymentAllocationCreate(
            project_id=payload.project_id,
            estimate_id=payload.estimate_id,
            amount=payload.amount,
        )
    ]


def create_payment_record(
    db: Session,
    *,
    company_id: str,
    user_id: str,
    payload: PaymentCreate,
) -> Payment:
    validate_positive_amount(payload.amount, message="Износот на уплатата мора да биде позитивен.")
    validate_payment_method(payload.payment_method)
    validate_payment_status(payload.status)
    _, project, _ = validate_payment_links(db, company_id=company_id, payload=payload)

    raw_allocations = payment_allocations_for_payload(payload)
    allocations = [
        validate_payment_allocation(
            db,
            company_id=company_id,
            payment_project_id=project.id,
            payload=allocation,
        )
        for allocation in raw_allocations
    ]
    allocation_total = round(sum(allocation.amount for allocation in allocations), 4)
    if allocation_total != round(payload.amount, 4):
        raise validation_error("Алокациите мора да го покријат целиот износ на уплатата.")

    payment = Payment(
        company_id=company_id,
        customer_id=payload.customer_id,
        project_id=project.id,
        estimate_id=payload.estimate_id,
        amount=payload.amount,
        payment_method=payload.payment_method,
        payment_date=payload.payment_date,
        status=payload.status,
        note=payload.note,
        created_by_user_id=user_id,
    )
    db.add(payment)
    db.flush()
    for allocation in allocations:
        db.add(
            PaymentAllocation(
                company_id=company_id,
                payment_id=payment.id,
                project_id=allocation.project_id,
                estimate_id=allocation.estimate_id,
                amount=allocation.amount,
                note=allocation.note,
            )
        )
    return payment


def get_payment_for_company(
    db: Session,
    *,
    company_id: str,
    payment_id: str,
) -> Payment:
    payment = (
        db.query(Payment)
        .filter(Payment.id == payment_id, Payment.company_id == company_id)
        .one_or_none()
    )
    if payment is None:
        raise not_found()
    return payment


def get_active_payment_for_company(
    db: Session,
    *,
    company_id: str,
    payment_id: str,
) -> Payment:
    payment = (
        db.query(Payment)
        .filter(
            Payment.id == payment_id,
            Payment.company_id == company_id,
            Payment.archived_at.is_(None),
        )
        .one_or_none()
    )
    if payment is None:
        raise not_found()
    return payment


def reverse_payment(payment: Payment, *, reason: str, user_id: str) -> Payment:
    if payment.status == "reversed":
        raise validation_error("Уплатата веќе е сторнирана.")
    payment.status = "reversed"
    payment.reversal_reason = reason
    payment.reversed_at = datetime.utcnow()
    payment.reversed_by_user_id = user_id
    return payment


def archive_payment(payment: Payment) -> Payment:
    payment.status = validate_payment_status("archived", allow_archived=True)
    payment.archived_at = datetime.utcnow()
    return payment


def get_expense_category_for_company(
    db: Session,
    *,
    company_id: str,
    category_id: str,
) -> ExpenseCategory:
    category = (
        db.query(ExpenseCategory)
        .filter(
            ExpenseCategory.id == category_id,
            ExpenseCategory.company_id == company_id,
            ExpenseCategory.archived_at.is_(None),
        )
        .one_or_none()
    )
    if category is None:
        raise not_found()
    return category


def validate_supplier(db: Session, *, company_id: str, supplier_id: Optional[str]) -> None:
    if supplier_id is None:
        return
    supplier = (
        db.query(Supplier)
        .filter(
            Supplier.id == supplier_id,
            Supplier.company_id == company_id,
            Supplier.archived_at.is_(None),
        )
        .one_or_none()
    )
    if supplier is None:
        raise validation_error("Добавувачот не е достапен за оваа компанија.")


def validate_material(db: Session, *, company_id: str, material_id: Optional[str]) -> None:
    if material_id is None:
        return
    material = (
        db.query(Material)
        .filter(
            Material.id == material_id,
            Material.company_id == company_id,
            Material.archived_at.is_(None),
        )
        .one_or_none()
    )
    if material is None:
        raise validation_error("Материјалот не е достапен за оваа компанија.")


def create_expense_record(
    db: Session,
    *,
    company_id: str,
    user_id: str,
    payload: ExpenseCreate,
) -> Expense:
    validate_positive_amount(payload.amount, message="Износот на трошокот мора да биде позитивен.")
    validate_payment_method(payload.payment_method)
    validate_expense_status(payload.status)
    if payload.project_id is not None:
        get_active_project_for_company(db, company_id=company_id, project_id=payload.project_id)
    if payload.category_id is not None:
        get_expense_category_for_company(
            db,
            company_id=company_id,
            category_id=payload.category_id,
        )
    validate_supplier(db, company_id=company_id, supplier_id=payload.supplier_id)
    validate_material(db, company_id=company_id, material_id=payload.material_id)

    expense = Expense(
        company_id=company_id,
        project_id=payload.project_id,
        category_id=payload.category_id,
        supplier_id=payload.supplier_id,
        material_id=payload.material_id,
        description=payload.description,
        amount=payload.amount,
        expense_date=payload.expense_date,
        payment_method=payload.payment_method,
        status=payload.status,
        note=payload.note,
        created_by_user_id=user_id,
    )
    db.add(expense)
    return expense


def get_expense_for_company(
    db: Session,
    *,
    company_id: str,
    expense_id: str,
) -> Expense:
    expense = (
        db.query(Expense)
        .filter(Expense.id == expense_id, Expense.company_id == company_id)
        .one_or_none()
    )
    if expense is None:
        raise not_found()
    return expense


def get_active_expense_for_company(
    db: Session,
    *,
    company_id: str,
    expense_id: str,
) -> Expense:
    expense = (
        db.query(Expense)
        .filter(
            Expense.id == expense_id,
            Expense.company_id == company_id,
            Expense.archived_at.is_(None),
        )
        .one_or_none()
    )
    if expense is None:
        raise not_found()
    return expense


def reverse_expense(expense: Expense, *, reason: str, user_id: str) -> Expense:
    if expense.status == "reversed":
        raise validation_error("Трошокот веќе е сторниран.")
    expense.status = "reversed"
    expense.reversal_reason = reason
    expense.reversed_at = datetime.utcnow()
    expense.reversed_by_user_id = user_id
    return expense


def archive_expense(expense: Expense) -> Expense:
    expense.status = validate_expense_status("archived", allow_archived=True)
    expense.archived_at = datetime.utcnow()
    return expense


def accepted_estimate_total_for_project(
    db: Session,
    *,
    company_id: str,
    project_id: str,
) -> Optional[float]:
    revision = (
        db.query(EstimateRevision)
        .join(Estimate, EstimateRevision.estimate_id == Estimate.id)
        .filter(
            Estimate.company_id == company_id,
            Estimate.project_id == project_id,
            Estimate.status == "accepted",
            Estimate.archived_at.is_(None),
            EstimateRevision.company_id == company_id,
            EstimateRevision.status == "accepted",
            EstimateRevision.archived_at.is_(None),
        )
        .order_by(EstimateRevision.accepted_at.desc(), EstimateRevision.created_at.desc())
        .first()
    )
    if revision is None:
        return None
    return calculate_revision_totals(revision)["total"]


def payment_sum(
    db: Session,
    *,
    company_id: str,
    project_id: str,
    status_value: str,
) -> float:
    value = (
        db.query(func.coalesce(func.sum(Payment.amount), 0.0))
        .filter(
            Payment.company_id == company_id,
            Payment.project_id == project_id,
            Payment.status == status_value,
            Payment.archived_at.is_(None),
        )
        .scalar()
    )
    return round(float(value or 0.0), 4)


def expense_sum(
    db: Session,
    *,
    company_id: str,
    project_id: str,
    statuses: set[str],
) -> float:
    value = (
        db.query(func.coalesce(func.sum(Expense.amount), 0.0))
        .filter(
            Expense.company_id == company_id,
            Expense.project_id == project_id,
            Expense.status.in_(statuses),
            Expense.archived_at.is_(None),
        )
        .scalar()
    )
    return round(float(value or 0.0), 4)


def payment_status_for(*, revenue_basis_amount: Optional[float], received: float) -> str:
    if revenue_basis_amount is None:
        return "unknown"
    if received == 0:
        return "unpaid"
    if round(received, 4) < round(revenue_basis_amount, 4):
        return "partially_paid"
    if round(received, 4) == round(revenue_basis_amount, 4):
        return "paid"
    return "overpaid"


def project_financial_summary(
    db: Session,
    *,
    company_id: str,
    project_id: str,
) -> dict[str, object]:
    project = get_active_project_for_company(db, company_id=company_id, project_id=project_id)
    accepted_total = accepted_estimate_total_for_project(
        db,
        company_id=company_id,
        project_id=project.id,
    )
    agreed_project_price = project.agreed_project_price
    if accepted_total is not None:
        revenue_basis = "accepted_estimate"
        revenue_basis_amount = accepted_total
    elif agreed_project_price is not None:
        revenue_basis = "agreed_project_price"
        revenue_basis_amount = agreed_project_price
    else:
        revenue_basis = "unknown"
        revenue_basis_amount = None

    received = payment_sum(
        db,
        company_id=company_id,
        project_id=project.id,
        status_value="received",
    )
    pending = payment_sum(db, company_id=company_id, project_id=project.id, status_value="pending")
    reversed_total = payment_sum(
        db,
        company_id=company_id,
        project_id=project.id,
        status_value="reversed",
    )
    recorded_expenses = expense_sum(
        db,
        company_id=company_id,
        project_id=project.id,
        statuses={"recorded", "reimbursed"},
    )
    reversed_expenses = expense_sum(
        db,
        company_id=company_id,
        project_id=project.id,
        statuses={"reversed"},
    )
    outstanding_balance = (
        None if revenue_basis_amount is None else round(revenue_basis_amount - received, 4)
    )
    profit_basis = revenue_basis_amount if revenue_basis_amount is not None else received
    estimated_profit = (
        None
        if profit_basis == 0 and revenue_basis_amount is None
        else round(profit_basis - recorded_expenses, 4)
    )

    return {
        "project_id": project.id,
        "customer_id": project.customer_id,
        "accepted_estimate_total": accepted_total,
        "agreed_project_price": agreed_project_price,
        "revenue_basis": revenue_basis,
        "total_received_payments": received,
        "total_pending_payments": pending,
        "total_reversed_payments": reversed_total,
        "outstanding_balance": outstanding_balance,
        "total_recorded_expenses": recorded_expenses,
        "total_reversed_expenses": reversed_expenses,
        "estimated_profit": estimated_profit,
        "payment_status": payment_status_for(
            revenue_basis_amount=revenue_basis_amount,
            received=received,
        ),
    }
