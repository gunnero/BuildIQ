from datetime import datetime
from typing import Any, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.calculation import CalculationLineItem, CalculationRun
from app.models.estimate import Estimate, EstimateItem, EstimateRevision
from app.models.material import Material
from app.models.project import Project
from app.schemas.estimate import (
    EstimateCreate,
    EstimateFromCalculationCreate,
    EstimateItemCreate,
    EstimateItemUpdate,
)
from app.services.customers import not_found
from app.services.projects import get_active_project_for_company

ESTIMATE_STATUSES = {"draft", "sent", "accepted", "rejected", "archived"}
ESTIMATE_ITEM_TYPES = {"material", "labor", "service", "discount", "adjustment"}
LOCKED_REVISION_STATUSES = {"sent", "accepted"}


def validation_error(message: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


def validate_estimate_status(value: str, *, allow_archived: bool = False) -> str:
    if value not in ESTIMATE_STATUSES:
        raise validation_error("Невалиден статус на понуда.")
    if value == "archived" and not allow_archived:
        raise validation_error("Користете ја архивската постапка за архивирање понуда.")
    return value


def validate_item_type(value: str) -> str:
    if value not in ESTIMATE_ITEM_TYPES:
        raise validation_error("Невалиден тип на ставка во понуда.")
    return value


def validate_non_negative_number(value: float, message: str) -> float:
    if value < 0:
        raise validation_error(message)
    return value


def get_estimate_for_company(
    db: Session,
    *,
    company_id: str,
    estimate_id: str,
) -> Estimate:
    estimate = (
        db.query(Estimate)
        .filter(
            Estimate.id == estimate_id,
            Estimate.company_id == company_id,
        )
        .one_or_none()
    )
    if estimate is None:
        raise not_found()
    return estimate


def get_active_estimate_for_company(
    db: Session,
    *,
    company_id: str,
    estimate_id: str,
) -> Estimate:
    estimate = (
        db.query(Estimate)
        .filter(
            Estimate.id == estimate_id,
            Estimate.company_id == company_id,
            Estimate.archived_at.is_(None),
        )
        .one_or_none()
    )
    if estimate is None:
        raise not_found()
    return estimate


def get_revision_for_company(
    db: Session,
    *,
    company_id: str,
    revision_id: str,
) -> EstimateRevision:
    revision = (
        db.query(EstimateRevision)
        .join(Estimate, EstimateRevision.estimate_id == Estimate.id)
        .filter(
            EstimateRevision.id == revision_id,
            EstimateRevision.company_id == company_id,
            EstimateRevision.archived_at.is_(None),
            Estimate.company_id == company_id,
            Estimate.archived_at.is_(None),
        )
        .one_or_none()
    )
    if revision is None:
        raise not_found()
    return revision


def get_item_for_company(
    db: Session,
    *,
    company_id: str,
    item_id: str,
) -> EstimateItem:
    item = (
        db.query(EstimateItem)
        .join(EstimateRevision, EstimateItem.estimate_revision_id == EstimateRevision.id)
        .join(Estimate, EstimateRevision.estimate_id == Estimate.id)
        .filter(
            EstimateItem.id == item_id,
            EstimateItem.company_id == company_id,
            EstimateItem.archived_at.is_(None),
            EstimateRevision.company_id == company_id,
            EstimateRevision.archived_at.is_(None),
            Estimate.company_id == company_id,
            Estimate.archived_at.is_(None),
        )
        .one_or_none()
    )
    if item is None:
        raise not_found()
    return item


def ensure_material_belongs_to_company(
    db: Session,
    *,
    company_id: str,
    material_id: Optional[str],
) -> None:
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


def ensure_revision_editable(revision: EstimateRevision) -> None:
    if revision.status in LOCKED_REVISION_STATUSES:
        raise validation_error("Испратена или прифатена понуда бара нова ревизија за измени.")


def ensure_estimate_editable(estimate: Estimate) -> None:
    revision = latest_revision(estimate)
    if estimate.status in LOCKED_REVISION_STATUSES or (
        revision is not None and revision.status in LOCKED_REVISION_STATUSES
    ):
        raise validation_error("Испратена или прифатена понуда бара нова ревизија за измени.")


def validate_project_link(
    db: Session,
    *,
    company_id: str,
    payload: EstimateCreate,
) -> Project:
    project = get_active_project_for_company(
        db,
        company_id=company_id,
        project_id=payload.project_id,
    )
    if payload.customer_id is not None and payload.customer_id != project.customer_id:
        raise validation_error("Клиентот не одговара на избраниот проект.")
    if payload.property_id is not None and payload.property_id != project.property_id:
        raise validation_error("Имотот не одговара на избраниот проект.")
    return project


def next_revision_number(db: Session, *, estimate_id: str, company_id: str) -> int:
    latest = (
        db.query(EstimateRevision)
        .filter(
            EstimateRevision.estimate_id == estimate_id,
            EstimateRevision.company_id == company_id,
        )
        .order_by(EstimateRevision.revision_number.desc())
        .first()
    )
    return 1 if latest is None else latest.revision_number + 1


def create_initial_revision(
    db: Session,
    *,
    estimate: Estimate,
    source_calculation_run_id: Optional[str] = None,
) -> EstimateRevision:
    revision = EstimateRevision(
        company_id=estimate.company_id,
        estimate_id=estimate.id,
        revision_number=next_revision_number(
            db,
            estimate_id=estimate.id,
            company_id=estimate.company_id,
        ),
        status="draft",
        source_calculation_run_id=source_calculation_run_id,
    )
    db.add(revision)
    db.flush()
    return revision


def calculate_item_total(quantity: float, unit_price: float) -> float:
    return round(quantity * unit_price, 4)


def calculate_revision_totals(revision: EstimateRevision) -> dict[str, float]:
    subtotal = 0.0
    discount_total = 0.0
    adjustment_total = 0.0
    for item in revision.items:
        if item.archived_at is not None:
            continue
        total_price = item.total_price or 0.0
        if item.item_type == "discount":
            discount_total += abs(total_price)
        elif item.item_type == "adjustment":
            adjustment_total += total_price
        else:
            subtotal += total_price

    tax_total = 0.0
    total = subtotal - discount_total + adjustment_total + tax_total
    return {
        "subtotal": round(subtotal, 4),
        "discount_total": round(discount_total, 4),
        "adjustment_total": round(adjustment_total, 4),
        "tax_total": round(tax_total, 4),
        "total": round(total, 4),
    }


def create_estimate(
    db: Session,
    *,
    company_id: str,
    payload: EstimateCreate,
    source_calculation_run_id: Optional[str] = None,
) -> Estimate:
    project = validate_project_link(db, company_id=company_id, payload=payload)
    estimate = Estimate(
        company_id=company_id,
        customer_id=project.customer_id,
        property_id=project.property_id,
        project_id=project.id,
        title=payload.title,
        description=payload.description,
        status="draft",
        source_calculation_run_id=source_calculation_run_id,
    )
    db.add(estimate)
    db.flush()
    create_initial_revision(
        db,
        estimate=estimate,
        source_calculation_run_id=source_calculation_run_id,
    )
    return estimate


def latest_revision(estimate: Estimate) -> Optional[EstimateRevision]:
    active_revisions = [
        revision for revision in estimate.revisions if revision.archived_at is None
    ]
    if not active_revisions:
        return None
    return sorted(active_revisions, key=lambda revision: revision.revision_number)[-1]


def change_estimate_status(
    estimate: Estimate,
    *,
    status_value: str,
) -> Estimate:
    status_value = validate_estimate_status(status_value)
    now = datetime.utcnow()
    estimate.status = status_value
    revision = latest_revision(estimate)
    if revision is not None:
        revision.status = status_value
    if status_value == "sent":
        estimate.sent_at = now
        if revision is not None:
            revision.sent_at = now
    elif status_value == "accepted":
        estimate.accepted_at = now
        if revision is not None:
            revision.accepted_at = now
    elif status_value == "rejected":
        estimate.rejected_at = now
        if revision is not None:
            revision.rejected_at = now
    return estimate


def archive_estimate(estimate: Estimate) -> Estimate:
    estimate.status = validate_estimate_status("archived", allow_archived=True)
    estimate.archived_at = datetime.utcnow()
    return estimate


def create_estimate_item(
    db: Session,
    *,
    company_id: str,
    revision: EstimateRevision,
    payload: EstimateItemCreate,
    source_calculation_run_id: Optional[str] = None,
    source_calculation_line_item_id: Optional[str] = None,
    sort_order: Optional[int] = None,
    total_price: Optional[float] = None,
) -> EstimateItem:
    ensure_revision_editable(revision)
    item_type = validate_item_type(payload.item_type)
    ensure_material_belongs_to_company(db, company_id=company_id, material_id=payload.material_id)
    quantity = validate_non_negative_number(payload.quantity, "Количината мора да биде позитивна.")
    unit_price = validate_non_negative_number(payload.unit_price, "Единечната цена мора да биде позитивна.")
    if sort_order is None:
        sort_order = (
            db.query(EstimateItem)
            .filter(
                EstimateItem.company_id == company_id,
                EstimateItem.estimate_revision_id == revision.id,
            )
            .count()
        )
    item = EstimateItem(
        company_id=company_id,
        estimate_revision_id=revision.id,
        item_type=item_type,
        name=payload.name,
        description=payload.description,
        material_id=payload.material_id,
        quantity=quantity,
        unit=payload.unit,
        unit_price=unit_price,
        total_price=calculate_item_total(quantity, unit_price) if total_price is None else total_price,
        source_calculation_run_id=source_calculation_run_id,
        source_calculation_line_item_id=source_calculation_line_item_id,
        sort_order=sort_order,
    )
    db.add(item)
    return item


def update_estimate_item(
    db: Session,
    *,
    company_id: str,
    item: EstimateItem,
    payload: EstimateItemUpdate,
) -> EstimateItem:
    ensure_revision_editable(item.revision)
    if payload.item_type is not None:
        item.item_type = validate_item_type(payload.item_type)
    if payload.material_id is not None:
        ensure_material_belongs_to_company(
            db,
            company_id=company_id,
            material_id=payload.material_id,
        )
        item.material_id = payload.material_id
    if payload.name is not None:
        item.name = payload.name
    if payload.description is not None:
        item.description = payload.description
    if payload.quantity is not None:
        item.quantity = validate_non_negative_number(
            payload.quantity,
            "Количината мора да биде позитивна.",
        )
    if payload.unit is not None:
        item.unit = payload.unit
    if payload.unit_price is not None:
        item.unit_price = validate_non_negative_number(
            payload.unit_price,
            "Единечната цена мора да биде позитивна.",
        )
    item.total_price = calculate_item_total(item.quantity, item.unit_price)
    return item


def archive_estimate_item(item: EstimateItem) -> EstimateItem:
    ensure_revision_editable(item.revision)
    item.archived_at = datetime.utcnow()
    return item


def get_completed_calculation_for_company(
    db: Session,
    *,
    company_id: str,
    calculation_run_id: str,
) -> CalculationRun:
    calculation_run = (
        db.query(CalculationRun)
        .filter(
            CalculationRun.id == calculation_run_id,
            CalculationRun.company_id == company_id,
        )
        .one_or_none()
    )
    if calculation_run is None:
        raise not_found()
    if calculation_run.status != "completed":
        raise validation_error("Понуда може да се креира само од завршена пресметка.")
    if calculation_run.project_id is None:
        raise validation_error("Пресметката мора да биде поврзана со проект.")
    return calculation_run


def payload_float(payload: dict[str, Any], *keys: str) -> Optional[float]:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, (int, float)):
            return float(value)
    return None


def infer_item_type(line_item: CalculationLineItem) -> str:
    payload = line_item.payload or {}
    if payload.get("material_id"):
        return "material"
    if "labor" in line_item.name.lower():
        return "labor"
    return "service"


def copy_calculation_line_item(
    db: Session,
    *,
    company_id: str,
    revision: EstimateRevision,
    calculation_run: CalculationRun,
    line_item: CalculationLineItem,
    sort_order: int,
) -> EstimateItem:
    payload = line_item.payload or {}
    quantity = float(line_item.quantity or 0.0)
    total = payload_float(payload, "total_cost", "total_price", "amount")
    unit_price = payload_float(payload, "unit_price")
    if unit_price is None and total is not None and quantity > 0:
        unit_price = total / quantity
    if unit_price is None:
        unit_price = 0.0
    if total is None:
        total = calculate_item_total(quantity, unit_price)
    item_payload = EstimateItemCreate(
        item_type=infer_item_type(line_item),
        name=line_item.name,
        description=line_item.description,
        material_id=payload.get("material_id"),
        quantity=quantity,
        unit=line_item.unit,
        unit_price=unit_price,
    )
    return create_estimate_item(
        db,
        company_id=company_id,
        revision=revision,
        payload=item_payload,
        source_calculation_run_id=calculation_run.id,
        source_calculation_line_item_id=line_item.id,
        sort_order=sort_order,
        total_price=round(total, 4),
    )


def create_estimate_from_calculation(
    db: Session,
    *,
    company_id: str,
    calculation_run_id: str,
    payload: EstimateFromCalculationCreate,
) -> Estimate:
    calculation_run = get_completed_calculation_for_company(
        db,
        company_id=company_id,
        calculation_run_id=calculation_run_id,
    )
    project = get_active_project_for_company(
        db,
        company_id=company_id,
        project_id=calculation_run.project_id,
    )
    estimate_payload = EstimateCreate(
        project_id=project.id,
        title=payload.title or f"{calculation_run.engine_type.title()} estimate",
        description=payload.description,
    )
    estimate = create_estimate(
        db,
        company_id=company_id,
        payload=estimate_payload,
        source_calculation_run_id=calculation_run.id,
    )
    revision = latest_revision(estimate)
    if revision is None:
        raise validation_error("Не може да се креира ревизија на понуда.")
    for index, line_item in enumerate(
        sorted(calculation_run.line_items, key=lambda item: item.sort_order)
    ):
        copy_calculation_line_item(
            db,
            company_id=company_id,
            revision=revision,
            calculation_run=calculation_run,
            line_item=line_item,
            sort_order=index,
        )
    return estimate
