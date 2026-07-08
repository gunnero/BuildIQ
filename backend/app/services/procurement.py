from datetime import date, datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.material import Material
from app.models.procurement import (
    PriceBook,
    PriceBookItem,
    ProjectMaterialPriceOverride,
    Supplier,
    SupplierAgreement,
    SupplierContact,
)
from app.schemas.procurement import ResolvedPriceResponse
from app.services.customers import not_found
from app.services.materials import get_active_material_for_company
from app.services.projects import get_active_project_for_company

SUPPLIER_TYPES = {"supplier", "store"}
SUPPLIER_STATUSES = {"active", "inactive", "archived"}
SUPPLIER_AGREEMENT_STATUSES = {
    "draft",
    "active",
    "paused",
    "expired",
    "cancelled",
    "archived",
}
PRICE_BOOK_TYPES = {"retail", "default", "negotiated"}
PRICE_BOOK_STATUSES = {"draft", "active", "archived"}


def validation_error(message: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


def validate_supplier_type(value: str) -> str:
    if value not in SUPPLIER_TYPES:
        raise validation_error("Невалиден тип на добавувач.")
    return value


def validate_supplier_status(value: str, *, allow_archived: bool = False) -> str:
    if value not in SUPPLIER_STATUSES:
        raise validation_error("Невалиден статус на добавувач.")
    if value == "archived" and not allow_archived:
        raise validation_error("Користете ја архивската постапка за архивирање добавувач.")
    return value


def validate_supplier_agreement_status(value: str, *, allow_archived: bool = False) -> str:
    if value not in SUPPLIER_AGREEMENT_STATUSES:
        raise validation_error("Невалиден статус на договор со добавувач.")
    if value == "archived" and not allow_archived:
        raise validation_error("Користете ја архивската постапка за архивирање договор.")
    return value


def validate_price_book_type(value: str) -> str:
    if value not in PRICE_BOOK_TYPES:
        raise validation_error("Невалиден тип на ценовник.")
    return value


def validate_price_book_status(value: str, *, allow_archived: bool = False) -> str:
    if value not in PRICE_BOOK_STATUSES:
        raise validation_error("Невалиден статус на ценовник.")
    if value == "archived" and not allow_archived:
        raise validation_error("Користете ја архивската постапка за архивирање ценовник.")
    return value


def ensure_valid_date_window(valid_from: Optional[date], valid_until: Optional[date]) -> None:
    if valid_from is not None and valid_until is not None and valid_until < valid_from:
        raise validation_error("Крајниот датум не може да биде пред почетниот датум.")


def get_active_supplier_for_company(
    db: Session,
    *,
    company_id: str,
    supplier_id: str,
) -> Supplier:
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
        raise not_found()
    return supplier


def get_active_supplier_contact_for_company(
    db: Session,
    *,
    company_id: str,
    contact_id: str,
) -> SupplierContact:
    contact = (
        db.query(SupplierContact)
        .join(Supplier, SupplierContact.supplier_id == Supplier.id)
        .filter(
            SupplierContact.id == contact_id,
            SupplierContact.company_id == company_id,
            SupplierContact.archived_at.is_(None),
            Supplier.company_id == company_id,
            Supplier.archived_at.is_(None),
        )
        .one_or_none()
    )
    if contact is None:
        raise not_found()
    return contact


def get_active_supplier_agreement_for_company(
    db: Session,
    *,
    company_id: str,
    agreement_id: str,
) -> SupplierAgreement:
    agreement = (
        db.query(SupplierAgreement)
        .join(Supplier, SupplierAgreement.supplier_id == Supplier.id)
        .filter(
            SupplierAgreement.id == agreement_id,
            SupplierAgreement.company_id == company_id,
            SupplierAgreement.archived_at.is_(None),
            Supplier.company_id == company_id,
            Supplier.archived_at.is_(None),
        )
        .one_or_none()
    )
    if agreement is None:
        raise not_found()
    return agreement


def get_active_price_book_for_company(
    db: Session,
    *,
    company_id: str,
    price_book_id: str,
) -> PriceBook:
    price_book = (
        db.query(PriceBook)
        .filter(
            PriceBook.id == price_book_id,
            PriceBook.company_id == company_id,
            PriceBook.archived_at.is_(None),
        )
        .one_or_none()
    )
    if price_book is None:
        raise not_found()
    return price_book


def get_active_price_book_item_for_company(
    db: Session,
    *,
    company_id: str,
    item_id: str,
) -> PriceBookItem:
    item = (
        db.query(PriceBookItem)
        .join(PriceBook, PriceBookItem.price_book_id == PriceBook.id)
        .join(Material, PriceBookItem.material_id == Material.id)
        .filter(
            PriceBookItem.id == item_id,
            PriceBookItem.company_id == company_id,
            PriceBookItem.archived_at.is_(None),
            PriceBook.company_id == company_id,
            PriceBook.archived_at.is_(None),
            Material.company_id == company_id,
            Material.archived_at.is_(None),
        )
        .one_or_none()
    )
    if item is None:
        raise not_found()
    return item


def get_active_material_price_override_for_company(
    db: Session,
    *,
    company_id: str,
    override_id: str,
) -> ProjectMaterialPriceOverride:
    override = (
        db.query(ProjectMaterialPriceOverride)
        .join(Material, ProjectMaterialPriceOverride.material_id == Material.id)
        .filter(
            ProjectMaterialPriceOverride.id == override_id,
            ProjectMaterialPriceOverride.company_id == company_id,
            ProjectMaterialPriceOverride.archived_at.is_(None),
            Material.company_id == company_id,
            Material.archived_at.is_(None),
        )
        .one_or_none()
    )
    if override is None:
        raise not_found()
    return override


def validate_supplier_parent(
    db: Session,
    *,
    company_id: str,
    parent_supplier_id: Optional[str],
) -> None:
    if parent_supplier_id is None:
        return
    get_active_supplier_for_company(
        db,
        company_id=company_id,
        supplier_id=parent_supplier_id,
    )


def validate_price_book_links(
    db: Session,
    *,
    company_id: str,
    supplier_id: Optional[str],
    supplier_agreement_id: Optional[str],
) -> Optional[str]:
    effective_supplier_id = supplier_id
    if supplier_id is not None:
        get_active_supplier_for_company(db, company_id=company_id, supplier_id=supplier_id)
    if supplier_agreement_id is not None:
        agreement = get_active_supplier_agreement_for_company(
            db,
            company_id=company_id,
            agreement_id=supplier_agreement_id,
        )
        if supplier_id is not None and agreement.supplier_id != supplier_id:
            raise validation_error("Договорот не припаѓа на избраниот добавувач.")
        effective_supplier_id = agreement.supplier_id
    return effective_supplier_id


def validate_price_book_item_links(
    db: Session,
    *,
    company_id: str,
    price_book: PriceBook,
    material_id: str,
    supplier_id: Optional[str],
) -> Optional[str]:
    get_active_material_for_company(db, company_id=company_id, material_id=material_id)
    effective_supplier_id = supplier_id if supplier_id is not None else price_book.supplier_id
    if effective_supplier_id is not None:
        get_active_supplier_for_company(
            db,
            company_id=company_id,
            supplier_id=effective_supplier_id,
        )
    if (
        price_book.supplier_id is not None
        and effective_supplier_id is not None
        and effective_supplier_id != price_book.supplier_id
    ):
        raise validation_error("Цената не припаѓа на добавувачот од ценовникот.")
    return effective_supplier_id


def validate_project_override_links(
    db: Session,
    *,
    company_id: str,
    project_id: str,
    material_id: str,
    supplier_id: Optional[str],
) -> None:
    get_active_project_for_company(db, company_id=company_id, project_id=project_id)
    get_active_material_for_company(db, company_id=company_id, material_id=material_id)
    if supplier_id is not None:
        get_active_supplier_for_company(db, company_id=company_id, supplier_id=supplier_id)


def active_on_date_filters(model: object, target_date: date) -> tuple[object, object]:
    return (
        model.valid_from <= target_date,
        or_(model.valid_until.is_(None), model.valid_until >= target_date),
    )


def resolved_none(*, material_id: str) -> ResolvedPriceResponse:
    return ResolvedPriceResponse(
        material_id=material_id,
        supplier_id=None,
        resolved_price=None,
        currency=None,
        source_type="none",
        source_id=None,
        valid_from=None,
        valid_until=None,
        notes=None,
    )


def resolve_material_price(
    db: Session,
    *,
    company_id: str,
    material_id: str,
    project_id: Optional[str] = None,
    target_date: Optional[date] = None,
) -> ResolvedPriceResponse:
    material = get_active_material_for_company(db, company_id=company_id, material_id=material_id)
    effective_date = target_date or date.today()

    if project_id is not None:
        project = get_active_project_for_company(db, company_id=company_id, project_id=project_id)
        override = (
            db.query(ProjectMaterialPriceOverride)
            .filter(
                ProjectMaterialPriceOverride.company_id == company_id,
                ProjectMaterialPriceOverride.project_id == project.id,
                ProjectMaterialPriceOverride.material_id == material.id,
                ProjectMaterialPriceOverride.archived_at.is_(None),
                *active_on_date_filters(ProjectMaterialPriceOverride, effective_date),
            )
            .order_by(
                ProjectMaterialPriceOverride.valid_from.desc(),
                ProjectMaterialPriceOverride.created_at.desc(),
            )
            .first()
        )
        if override is not None:
            return ResolvedPriceResponse(
                material_id=material.id,
                supplier_id=override.supplier_id,
                resolved_price=override.unit_price,
                currency=override.currency,
                source_type="project_override",
                source_id=override.id,
                valid_from=override.valid_from,
                valid_until=override.valid_until,
                notes=override.notes,
            )

    negotiated_item = find_price_book_item(
        db,
        company_id=company_id,
        material_id=material.id,
        price_types={"negotiated"},
        target_date=effective_date,
    )
    if negotiated_item is not None:
        return price_book_item_resolved_response(
            negotiated_item,
            source_type="negotiated_price_book",
        )

    retail_item = find_price_book_item(
        db,
        company_id=company_id,
        material_id=material.id,
        price_types={"retail", "default"},
        target_date=effective_date,
    )
    if retail_item is not None:
        return price_book_item_resolved_response(
            retail_item,
            source_type="retail_price_book",
        )

    return resolved_none(material_id=material.id)


def find_price_book_item(
    db: Session,
    *,
    company_id: str,
    material_id: str,
    price_types: set[str],
    target_date: date,
) -> Optional[PriceBookItem]:
    return (
        db.query(PriceBookItem)
        .join(PriceBook, PriceBookItem.price_book_id == PriceBook.id)
        .filter(
            PriceBookItem.company_id == company_id,
            PriceBookItem.material_id == material_id,
            PriceBookItem.archived_at.is_(None),
            PriceBook.company_id == company_id,
            PriceBook.archived_at.is_(None),
            PriceBook.status == "active",
            PriceBook.price_type.in_(price_types),
            *active_on_date_filters(PriceBookItem, target_date),
            *active_on_date_filters(PriceBook, target_date),
        )
        .order_by(
            PriceBookItem.valid_from.desc(),
            PriceBook.valid_from.desc(),
            PriceBookItem.created_at.desc(),
        )
        .first()
    )


def price_book_item_resolved_response(
    item: PriceBookItem,
    *,
    source_type: str,
) -> ResolvedPriceResponse:
    return ResolvedPriceResponse(
        material_id=item.material_id,
        supplier_id=item.supplier_id,
        resolved_price=item.unit_price,
        currency=item.currency,
        source_type=source_type,
        source_id=item.id,
        valid_from=item.valid_from,
        valid_until=item.valid_until,
        notes=item.notes,
    )


def archive_supplier(supplier: Supplier) -> Supplier:
    supplier.status = validate_supplier_status("archived", allow_archived=True)
    supplier.archived_at = datetime.utcnow()
    return supplier


def archive_supplier_contact(contact: SupplierContact) -> SupplierContact:
    contact.archived_at = datetime.utcnow()
    return contact


def archive_supplier_agreement(agreement: SupplierAgreement) -> SupplierAgreement:
    agreement.status = validate_supplier_agreement_status("archived", allow_archived=True)
    agreement.archived_at = datetime.utcnow()
    return agreement


def archive_price_book(price_book: PriceBook) -> PriceBook:
    price_book.status = validate_price_book_status("archived", allow_archived=True)
    price_book.archived_at = datetime.utcnow()
    return price_book


def archive_price_book_item(item: PriceBookItem) -> PriceBookItem:
    item.archived_at = datetime.utcnow()
    return item


def archive_material_price_override(
    override: ProjectMaterialPriceOverride,
) -> ProjectMaterialPriceOverride:
    override.archived_at = datetime.utcnow()
    return override
