from datetime import date

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_company, get_current_user
from app.db.session import get_db
from app.models.identity import Company, User
from app.models.procurement import (
    PriceBook,
    PriceBookItem,
    ProjectMaterialPriceOverride,
    Supplier,
    SupplierAgreement,
    SupplierContact,
)
from app.schemas.procurement import (
    PriceBookCreate,
    PriceBookItemCreate,
    PriceBookItemResponse,
    PriceBookItemUpdate,
    PriceBookResponse,
    PriceBookUpdate,
    ProjectMaterialPriceOverrideCreate,
    ProjectMaterialPriceOverrideResponse,
    ProjectMaterialPriceOverrideUpdate,
    ResolvedPriceResponse,
    SupplierAgreementCreate,
    SupplierAgreementResponse,
    SupplierAgreementUpdate,
    SupplierContactCreate,
    SupplierContactResponse,
    SupplierContactUpdate,
    SupplierCreate,
    SupplierResponse,
    SupplierUpdate,
)
from app.services.procurement import (
    archive_material_price_override,
    archive_price_book,
    archive_price_book_item,
    archive_supplier,
    archive_supplier_agreement,
    archive_supplier_contact,
    ensure_valid_date_window,
    get_active_material_price_override_for_company,
    get_active_price_book_for_company,
    get_active_price_book_item_for_company,
    get_active_supplier_agreement_for_company,
    get_active_supplier_contact_for_company,
    get_active_supplier_for_company,
    resolve_material_price,
    validate_price_book_item_links,
    validate_price_book_links,
    validate_price_book_status,
    validate_price_book_type,
    validate_project_override_links,
    validate_supplier_agreement_status,
    validate_supplier_parent,
    validate_supplier_status,
    validate_supplier_type,
)
from app.services.projects import get_active_project_for_company

router = APIRouter(tags=["procurement"])


def supplier_response(supplier: Supplier) -> SupplierResponse:
    return SupplierResponse(
        id=supplier.id,
        company_id=supplier.company_id,
        parent_supplier_id=supplier.parent_supplier_id,
        name=supplier.name,
        supplier_type=supplier.supplier_type,
        tax_number=supplier.tax_number,
        phone=supplier.phone,
        email=supplier.email,
        address=supplier.address,
        note=supplier.note,
        status=supplier.status,
        archived_at=supplier.archived_at,
    )


def supplier_contact_response(contact: SupplierContact) -> SupplierContactResponse:
    return SupplierContactResponse(
        id=contact.id,
        company_id=contact.company_id,
        supplier_id=contact.supplier_id,
        full_name=contact.full_name,
        phone=contact.phone,
        email=contact.email,
        role=contact.role,
        note=contact.note,
        is_primary=contact.is_primary,
        archived_at=contact.archived_at,
    )


def supplier_agreement_response(agreement: SupplierAgreement) -> SupplierAgreementResponse:
    return SupplierAgreementResponse(
        id=agreement.id,
        company_id=agreement.company_id,
        supplier_id=agreement.supplier_id,
        agreement_number=agreement.agreement_number,
        status=agreement.status,
        starts_on=agreement.starts_on,
        ends_on=agreement.ends_on,
        terms_snapshot=agreement.terms_snapshot,
        notes=agreement.notes,
        archived_at=agreement.archived_at,
    )


def price_book_response(price_book: PriceBook) -> PriceBookResponse:
    return PriceBookResponse(
        id=price_book.id,
        company_id=price_book.company_id,
        supplier_id=price_book.supplier_id,
        supplier_agreement_id=price_book.supplier_agreement_id,
        name=price_book.name,
        price_type=price_book.price_type,
        status=price_book.status,
        currency=price_book.currency,
        valid_from=price_book.valid_from,
        valid_until=price_book.valid_until,
        notes=price_book.notes,
        archived_at=price_book.archived_at,
    )


def price_book_item_response(item: PriceBookItem) -> PriceBookItemResponse:
    return PriceBookItemResponse(
        id=item.id,
        company_id=item.company_id,
        price_book_id=item.price_book_id,
        material_id=item.material_id,
        supplier_id=item.supplier_id,
        supplier_sku=item.supplier_sku,
        unit_price=item.unit_price,
        currency=item.currency,
        valid_from=item.valid_from,
        valid_until=item.valid_until,
        notes=item.notes,
        archived_at=item.archived_at,
    )


def material_price_override_response(
    override: ProjectMaterialPriceOverride,
) -> ProjectMaterialPriceOverrideResponse:
    return ProjectMaterialPriceOverrideResponse(
        id=override.id,
        company_id=override.company_id,
        project_id=override.project_id,
        material_id=override.material_id,
        supplier_id=override.supplier_id,
        unit_price=override.unit_price,
        currency=override.currency,
        valid_from=override.valid_from,
        valid_until=override.valid_until,
        reason=override.reason,
        notes=override.notes,
        created_by_user_id=override.created_by_user_id,
        archived_at=override.archived_at,
    )


@router.post("/suppliers", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
def create_supplier(
    payload: SupplierCreate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> SupplierResponse:
    validate_supplier_type(payload.supplier_type)
    validate_supplier_parent(
        db,
        company_id=company.id,
        parent_supplier_id=payload.parent_supplier_id,
    )
    supplier = Supplier(
        company_id=company.id,
        parent_supplier_id=payload.parent_supplier_id,
        name=payload.name,
        supplier_type=payload.supplier_type,
        tax_number=payload.tax_number,
        phone=payload.phone,
        email=payload.email,
        address=payload.address,
        note=payload.note,
        status="active",
    )
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier_response(supplier)


@router.get("/suppliers", response_model=list[SupplierResponse])
def list_suppliers(
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> list[SupplierResponse]:
    suppliers = (
        db.query(Supplier)
        .filter(Supplier.company_id == company.id, Supplier.archived_at.is_(None))
        .order_by(Supplier.created_at.asc())
        .all()
    )
    return [supplier_response(supplier) for supplier in suppliers]


@router.get("/suppliers/{supplier_id}", response_model=SupplierResponse)
def read_supplier(
    supplier_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> SupplierResponse:
    supplier = get_active_supplier_for_company(db, company_id=company.id, supplier_id=supplier_id)
    return supplier_response(supplier)


@router.patch("/suppliers/{supplier_id}", response_model=SupplierResponse)
def update_supplier(
    supplier_id: str,
    payload: SupplierUpdate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> SupplierResponse:
    supplier = get_active_supplier_for_company(db, company_id=company.id, supplier_id=supplier_id)
    values = payload.model_dump(exclude_unset=True)
    if values.get("supplier_type") is not None:
        validate_supplier_type(values["supplier_type"])
    if values.get("status") is not None:
        validate_supplier_status(values["status"])
    if "parent_supplier_id" in values:
        validate_supplier_parent(
            db,
            company_id=company.id,
            parent_supplier_id=values["parent_supplier_id"],
        )
    for field, value in values.items():
        setattr(supplier, field, value)
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier_response(supplier)


@router.post("/suppliers/{supplier_id}/archive", response_model=SupplierResponse)
def archive_supplier_endpoint(
    supplier_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> SupplierResponse:
    supplier = get_active_supplier_for_company(db, company_id=company.id, supplier_id=supplier_id)
    archive_supplier(supplier)
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier_response(supplier)


@router.post(
    "/suppliers/{supplier_id}/contacts",
    response_model=SupplierContactResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_supplier_contact(
    supplier_id: str,
    payload: SupplierContactCreate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> SupplierContactResponse:
    supplier = get_active_supplier_for_company(db, company_id=company.id, supplier_id=supplier_id)
    contact = SupplierContact(
        company_id=company.id,
        supplier_id=supplier.id,
        full_name=payload.full_name,
        phone=payload.phone,
        email=payload.email,
        role=payload.role,
        note=payload.note,
        is_primary=payload.is_primary,
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return supplier_contact_response(contact)


@router.get("/suppliers/{supplier_id}/contacts", response_model=list[SupplierContactResponse])
def list_supplier_contacts(
    supplier_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> list[SupplierContactResponse]:
    supplier = get_active_supplier_for_company(db, company_id=company.id, supplier_id=supplier_id)
    contacts = (
        db.query(SupplierContact)
        .filter(
            SupplierContact.company_id == company.id,
            SupplierContact.supplier_id == supplier.id,
            SupplierContact.archived_at.is_(None),
        )
        .order_by(SupplierContact.created_at.asc())
        .all()
    )
    return [supplier_contact_response(contact) for contact in contacts]


@router.patch("/supplier-contacts/{contact_id}", response_model=SupplierContactResponse)
def update_supplier_contact(
    contact_id: str,
    payload: SupplierContactUpdate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> SupplierContactResponse:
    contact = get_active_supplier_contact_for_company(
        db,
        company_id=company.id,
        contact_id=contact_id,
    )
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(contact, field, value)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return supplier_contact_response(contact)


@router.post("/supplier-contacts/{contact_id}/archive", response_model=SupplierContactResponse)
def archive_supplier_contact_endpoint(
    contact_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> SupplierContactResponse:
    contact = get_active_supplier_contact_for_company(
        db,
        company_id=company.id,
        contact_id=contact_id,
    )
    archive_supplier_contact(contact)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return supplier_contact_response(contact)


@router.post(
    "/suppliers/{supplier_id}/agreements",
    response_model=SupplierAgreementResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_supplier_agreement(
    supplier_id: str,
    payload: SupplierAgreementCreate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> SupplierAgreementResponse:
    supplier = get_active_supplier_for_company(db, company_id=company.id, supplier_id=supplier_id)
    validate_supplier_agreement_status(payload.status)
    ensure_valid_date_window(payload.starts_on, payload.ends_on)
    agreement = SupplierAgreement(
        company_id=company.id,
        supplier_id=supplier.id,
        agreement_number=payload.agreement_number,
        status=payload.status,
        starts_on=payload.starts_on,
        ends_on=payload.ends_on,
        terms_snapshot=payload.terms_snapshot,
        notes=payload.notes,
    )
    db.add(agreement)
    db.commit()
    db.refresh(agreement)
    return supplier_agreement_response(agreement)


@router.get("/suppliers/{supplier_id}/agreements", response_model=list[SupplierAgreementResponse])
def list_supplier_agreements(
    supplier_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> list[SupplierAgreementResponse]:
    supplier = get_active_supplier_for_company(db, company_id=company.id, supplier_id=supplier_id)
    agreements = (
        db.query(SupplierAgreement)
        .filter(
            SupplierAgreement.company_id == company.id,
            SupplierAgreement.supplier_id == supplier.id,
            SupplierAgreement.archived_at.is_(None),
        )
        .order_by(SupplierAgreement.created_at.asc())
        .all()
    )
    return [supplier_agreement_response(agreement) for agreement in agreements]


@router.get("/supplier-agreements/{agreement_id}", response_model=SupplierAgreementResponse)
def read_supplier_agreement(
    agreement_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> SupplierAgreementResponse:
    agreement = get_active_supplier_agreement_for_company(
        db,
        company_id=company.id,
        agreement_id=agreement_id,
    )
    return supplier_agreement_response(agreement)


@router.patch("/supplier-agreements/{agreement_id}", response_model=SupplierAgreementResponse)
def update_supplier_agreement(
    agreement_id: str,
    payload: SupplierAgreementUpdate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> SupplierAgreementResponse:
    agreement = get_active_supplier_agreement_for_company(
        db,
        company_id=company.id,
        agreement_id=agreement_id,
    )
    values = payload.model_dump(exclude_unset=True)
    if values.get("status") is not None:
        validate_supplier_agreement_status(values["status"])
    starts_on = values.get("starts_on", agreement.starts_on)
    ends_on = values.get("ends_on", agreement.ends_on)
    ensure_valid_date_window(starts_on, ends_on)
    for field, value in values.items():
        setattr(agreement, field, value)
    db.add(agreement)
    db.commit()
    db.refresh(agreement)
    return supplier_agreement_response(agreement)


@router.post("/supplier-agreements/{agreement_id}/archive", response_model=SupplierAgreementResponse)
def archive_supplier_agreement_endpoint(
    agreement_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> SupplierAgreementResponse:
    agreement = get_active_supplier_agreement_for_company(
        db,
        company_id=company.id,
        agreement_id=agreement_id,
    )
    archive_supplier_agreement(agreement)
    db.add(agreement)
    db.commit()
    db.refresh(agreement)
    return supplier_agreement_response(agreement)


@router.post("/price-books", response_model=PriceBookResponse, status_code=status.HTTP_201_CREATED)
def create_price_book(
    payload: PriceBookCreate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> PriceBookResponse:
    validate_price_book_type(payload.price_type)
    validate_price_book_status(payload.status)
    valid_from = payload.valid_from or date.today()
    ensure_valid_date_window(valid_from, payload.valid_until)
    effective_supplier_id = validate_price_book_links(
        db,
        company_id=company.id,
        supplier_id=payload.supplier_id,
        supplier_agreement_id=payload.supplier_agreement_id,
    )
    price_book = PriceBook(
        company_id=company.id,
        supplier_id=effective_supplier_id,
        supplier_agreement_id=payload.supplier_agreement_id,
        name=payload.name,
        price_type=payload.price_type,
        status=payload.status,
        currency=payload.currency,
        valid_from=valid_from,
        valid_until=payload.valid_until,
        notes=payload.notes,
    )
    db.add(price_book)
    db.commit()
    db.refresh(price_book)
    return price_book_response(price_book)


@router.get("/price-books", response_model=list[PriceBookResponse])
def list_price_books(
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> list[PriceBookResponse]:
    price_books = (
        db.query(PriceBook)
        .filter(PriceBook.company_id == company.id, PriceBook.archived_at.is_(None))
        .order_by(PriceBook.created_at.asc())
        .all()
    )
    return [price_book_response(price_book) for price_book in price_books]


@router.get("/price-books/{price_book_id}", response_model=PriceBookResponse)
def read_price_book(
    price_book_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> PriceBookResponse:
    price_book = get_active_price_book_for_company(
        db,
        company_id=company.id,
        price_book_id=price_book_id,
    )
    return price_book_response(price_book)


@router.patch("/price-books/{price_book_id}", response_model=PriceBookResponse)
def update_price_book(
    price_book_id: str,
    payload: PriceBookUpdate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> PriceBookResponse:
    price_book = get_active_price_book_for_company(
        db,
        company_id=company.id,
        price_book_id=price_book_id,
    )
    values = payload.model_dump(exclude_unset=True)
    if values.get("price_type") is not None:
        validate_price_book_type(values["price_type"])
    if values.get("status") is not None:
        validate_price_book_status(values["status"])
    valid_from = values.get("valid_from", price_book.valid_from)
    valid_until = values.get("valid_until", price_book.valid_until)
    ensure_valid_date_window(valid_from, valid_until)
    if "supplier_id" in values or "supplier_agreement_id" in values:
        values["supplier_id"] = validate_price_book_links(
            db,
            company_id=company.id,
            supplier_id=values.get("supplier_id", price_book.supplier_id),
            supplier_agreement_id=values.get(
                "supplier_agreement_id",
                price_book.supplier_agreement_id,
            ),
        )
    for field, value in values.items():
        setattr(price_book, field, value)
    db.add(price_book)
    db.commit()
    db.refresh(price_book)
    return price_book_response(price_book)


@router.post("/price-books/{price_book_id}/archive", response_model=PriceBookResponse)
def archive_price_book_endpoint(
    price_book_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> PriceBookResponse:
    price_book = get_active_price_book_for_company(
        db,
        company_id=company.id,
        price_book_id=price_book_id,
    )
    archive_price_book(price_book)
    db.add(price_book)
    db.commit()
    db.refresh(price_book)
    return price_book_response(price_book)


@router.post(
    "/price-books/{price_book_id}/items",
    response_model=PriceBookItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_price_book_item(
    price_book_id: str,
    payload: PriceBookItemCreate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> PriceBookItemResponse:
    price_book = get_active_price_book_for_company(
        db,
        company_id=company.id,
        price_book_id=price_book_id,
    )
    ensure_valid_date_window(payload.valid_from, payload.valid_until)
    effective_supplier_id = validate_price_book_item_links(
        db,
        company_id=company.id,
        price_book=price_book,
        material_id=payload.material_id,
        supplier_id=payload.supplier_id,
    )
    item = PriceBookItem(
        company_id=company.id,
        price_book_id=price_book.id,
        material_id=payload.material_id,
        supplier_id=effective_supplier_id,
        supplier_sku=payload.supplier_sku,
        unit_price=payload.unit_price,
        currency=payload.currency,
        valid_from=payload.valid_from,
        valid_until=payload.valid_until,
        notes=payload.notes,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return price_book_item_response(item)


@router.get("/price-books/{price_book_id}/items", response_model=list[PriceBookItemResponse])
def list_price_book_items(
    price_book_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> list[PriceBookItemResponse]:
    price_book = get_active_price_book_for_company(
        db,
        company_id=company.id,
        price_book_id=price_book_id,
    )
    items = (
        db.query(PriceBookItem)
        .filter(
            PriceBookItem.company_id == company.id,
            PriceBookItem.price_book_id == price_book.id,
            PriceBookItem.archived_at.is_(None),
        )
        .order_by(PriceBookItem.created_at.asc())
        .all()
    )
    return [price_book_item_response(item) for item in items]


@router.patch("/price-book-items/{item_id}", response_model=PriceBookItemResponse)
def update_price_book_item(
    item_id: str,
    payload: PriceBookItemUpdate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> PriceBookItemResponse:
    item = get_active_price_book_item_for_company(db, company_id=company.id, item_id=item_id)
    price_book = get_active_price_book_for_company(
        db,
        company_id=company.id,
        price_book_id=item.price_book_id,
    )
    values = payload.model_dump(exclude_unset=True)
    material_id = values.get("material_id", item.material_id)
    supplier_id = values.get("supplier_id", item.supplier_id)
    effective_supplier_id = validate_price_book_item_links(
        db,
        company_id=company.id,
        price_book=price_book,
        material_id=material_id,
        supplier_id=supplier_id,
    )
    values["supplier_id"] = effective_supplier_id
    valid_from = values.get("valid_from", item.valid_from)
    valid_until = values.get("valid_until", item.valid_until)
    ensure_valid_date_window(valid_from, valid_until)
    for field, value in values.items():
        setattr(item, field, value)
    db.add(item)
    db.commit()
    db.refresh(item)
    return price_book_item_response(item)


@router.post("/price-book-items/{item_id}/archive", response_model=PriceBookItemResponse)
def archive_price_book_item_endpoint(
    item_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> PriceBookItemResponse:
    item = get_active_price_book_item_for_company(db, company_id=company.id, item_id=item_id)
    archive_price_book_item(item)
    db.add(item)
    db.commit()
    db.refresh(item)
    return price_book_item_response(item)


@router.post(
    "/projects/{project_id}/material-price-overrides",
    response_model=ProjectMaterialPriceOverrideResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_material_price_override(
    project_id: str,
    payload: ProjectMaterialPriceOverrideCreate,
    company: Company = Depends(get_current_company),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectMaterialPriceOverrideResponse:
    validate_project_override_links(
        db,
        company_id=company.id,
        project_id=project_id,
        material_id=payload.material_id,
        supplier_id=payload.supplier_id,
    )
    ensure_valid_date_window(payload.valid_from, payload.valid_until)
    override = ProjectMaterialPriceOverride(
        company_id=company.id,
        project_id=project_id,
        material_id=payload.material_id,
        supplier_id=payload.supplier_id,
        unit_price=payload.unit_price,
        currency=payload.currency,
        valid_from=payload.valid_from,
        valid_until=payload.valid_until,
        reason=payload.reason,
        notes=payload.notes,
        created_by_user_id=current_user.id,
    )
    db.add(override)
    db.commit()
    db.refresh(override)
    return material_price_override_response(override)


@router.get(
    "/projects/{project_id}/material-price-overrides",
    response_model=list[ProjectMaterialPriceOverrideResponse],
)
def list_material_price_overrides(
    project_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> list[ProjectMaterialPriceOverrideResponse]:
    project = get_active_project_for_company(db, company_id=company.id, project_id=project_id)
    overrides = (
        db.query(ProjectMaterialPriceOverride)
        .filter(
            ProjectMaterialPriceOverride.company_id == company.id,
            ProjectMaterialPriceOverride.project_id == project.id,
            ProjectMaterialPriceOverride.archived_at.is_(None),
        )
        .order_by(ProjectMaterialPriceOverride.created_at.asc())
        .all()
    )
    return [material_price_override_response(override) for override in overrides]


@router.patch(
    "/material-price-overrides/{override_id}",
    response_model=ProjectMaterialPriceOverrideResponse,
)
def update_material_price_override(
    override_id: str,
    payload: ProjectMaterialPriceOverrideUpdate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> ProjectMaterialPriceOverrideResponse:
    override = get_active_material_price_override_for_company(
        db,
        company_id=company.id,
        override_id=override_id,
    )
    values = payload.model_dump(exclude_unset=True)
    validate_project_override_links(
        db,
        company_id=company.id,
        project_id=override.project_id,
        material_id=values.get("material_id", override.material_id),
        supplier_id=values.get("supplier_id", override.supplier_id),
    )
    valid_from = values.get("valid_from", override.valid_from)
    valid_until = values.get("valid_until", override.valid_until)
    ensure_valid_date_window(valid_from, valid_until)
    for field, value in values.items():
        setattr(override, field, value)
    db.add(override)
    db.commit()
    db.refresh(override)
    return material_price_override_response(override)


@router.post(
    "/material-price-overrides/{override_id}/archive",
    response_model=ProjectMaterialPriceOverrideResponse,
)
def archive_material_price_override_endpoint(
    override_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> ProjectMaterialPriceOverrideResponse:
    override = get_active_material_price_override_for_company(
        db,
        company_id=company.id,
        override_id=override_id,
    )
    archive_material_price_override(override)
    db.add(override)
    db.commit()
    db.refresh(override)
    return material_price_override_response(override)


@router.get("/materials/{material_id}/resolved-price", response_model=ResolvedPriceResponse)
def resolve_material_price_endpoint(
    material_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> ResolvedPriceResponse:
    return resolve_material_price(db, company_id=company.id, material_id=material_id)


@router.get(
    "/projects/{project_id}/materials/{material_id}/resolved-price",
    response_model=ResolvedPriceResponse,
)
def resolve_project_material_price_endpoint(
    project_id: str,
    material_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> ResolvedPriceResponse:
    return resolve_material_price(
        db,
        company_id=company.id,
        project_id=project_id,
        material_id=material_id,
    )
