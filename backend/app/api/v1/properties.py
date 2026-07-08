from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_company, get_current_user
from app.db.session import get_db
from app.models.customer import Property, PropertyContact, PropertyNote
from app.models.identity import Company, User
from app.models.kernel import AuditLog
from app.schemas.customer import (
    PropertyContactCreate,
    PropertyContactResponse,
    PropertyCreate,
    PropertyNoteCreate,
    PropertyNoteResponse,
    PropertyResponse,
    PropertyUpdate,
)
from app.services.customers import (
    archive_property,
    get_active_customer_for_company,
    get_active_property_for_company,
)

router = APIRouter(prefix="/properties", tags=["properties"])


def property_response(property_item: Property) -> PropertyResponse:
    return PropertyResponse(
        id=property_item.id,
        company_id=property_item.company_id,
        customer_id=property_item.customer_id,
        name=property_item.name,
        address=property_item.address,
        city=property_item.city,
        note=property_item.note,
        status=property_item.status,
        archived_at=property_item.archived_at,
    )


def property_contact_response(contact: PropertyContact) -> PropertyContactResponse:
    return PropertyContactResponse(
        id=contact.id,
        company_id=contact.company_id,
        property_id=contact.property_id,
        full_name=contact.full_name,
        phone=contact.phone,
        email=contact.email,
        role=contact.role,
        note=contact.note,
        is_primary=contact.is_primary,
        archived_at=contact.archived_at,
    )


def property_note_response(note: PropertyNote) -> PropertyNoteResponse:
    return PropertyNoteResponse(
        id=note.id,
        company_id=note.company_id,
        property_id=note.property_id,
        content=note.content,
        created_by_user_id=note.created_by_user_id,
        archived_at=note.archived_at,
    )


@router.post("", response_model=PropertyResponse, status_code=status.HTTP_201_CREATED)
def create_property(
    payload: PropertyCreate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> PropertyResponse:
    customer = get_active_customer_for_company(
        db,
        company_id=company.id,
        customer_id=payload.customer_id,
    )
    property_item = Property(
        company_id=company.id,
        customer_id=customer.id,
        name=payload.name,
        address=payload.address,
        city=payload.city,
        note=payload.note,
    )
    db.add(property_item)
    db.commit()
    db.refresh(property_item)
    return property_response(property_item)


@router.get("", response_model=list[PropertyResponse])
def list_properties(
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> list[PropertyResponse]:
    properties = (
        db.query(Property)
        .filter(Property.company_id == company.id, Property.archived_at.is_(None))
        .order_by(Property.created_at.asc())
        .all()
    )
    return [property_response(property_item) for property_item in properties]


@router.get("/{property_id}", response_model=PropertyResponse)
def read_property(
    property_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> PropertyResponse:
    property_item = get_active_property_for_company(
        db,
        company_id=company.id,
        property_id=property_id,
    )
    return property_response(property_item)


@router.patch("/{property_id}", response_model=PropertyResponse)
def update_property(
    property_id: str,
    payload: PropertyUpdate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> PropertyResponse:
    property_item = get_active_property_for_company(
        db,
        company_id=company.id,
        property_id=property_id,
    )
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(property_item, field, value)
    db.add(property_item)
    db.commit()
    db.refresh(property_item)
    return property_response(property_item)


@router.post("/{property_id}/archive", response_model=PropertyResponse)
def archive_property_endpoint(
    property_id: str,
    company: Company = Depends(get_current_company),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PropertyResponse:
    property_item = get_active_property_for_company(
        db,
        company_id=company.id,
        property_id=property_id,
    )
    archive_property(property_item)
    db.add(
        AuditLog(
            company_id=company.id,
            acting_user_id=current_user.id,
            entity_type="property",
            entity_id=property_item.id,
            action="archived",
        )
    )
    db.add(property_item)
    db.commit()
    db.refresh(property_item)
    return property_response(property_item)


@router.post(
    "/{property_id}/contacts",
    response_model=PropertyContactResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_property_contact(
    property_id: str,
    payload: PropertyContactCreate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> PropertyContactResponse:
    property_item = get_active_property_for_company(
        db,
        company_id=company.id,
        property_id=property_id,
    )
    contact = PropertyContact(
        company_id=company.id,
        property_id=property_item.id,
        **payload.model_dump(),
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return property_contact_response(contact)


@router.get("/{property_id}/contacts", response_model=list[PropertyContactResponse])
def list_property_contacts(
    property_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> list[PropertyContactResponse]:
    property_item = get_active_property_for_company(
        db,
        company_id=company.id,
        property_id=property_id,
    )
    contacts = (
        db.query(PropertyContact)
        .filter(
            PropertyContact.company_id == company.id,
            PropertyContact.property_id == property_item.id,
            PropertyContact.archived_at.is_(None),
        )
        .order_by(PropertyContact.created_at.asc())
        .all()
    )
    return [property_contact_response(contact) for contact in contacts]


@router.post(
    "/{property_id}/notes",
    response_model=PropertyNoteResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_property_note(
    property_id: str,
    payload: PropertyNoteCreate,
    company: Company = Depends(get_current_company),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PropertyNoteResponse:
    property_item = get_active_property_for_company(
        db,
        company_id=company.id,
        property_id=property_id,
    )
    note = PropertyNote(
        company_id=company.id,
        property_id=property_item.id,
        content=payload.content,
        created_by_user_id=current_user.id,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return property_note_response(note)


@router.get("/{property_id}/notes", response_model=list[PropertyNoteResponse])
def list_property_notes(
    property_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> list[PropertyNoteResponse]:
    property_item = get_active_property_for_company(
        db,
        company_id=company.id,
        property_id=property_id,
    )
    notes = (
        db.query(PropertyNote)
        .filter(
            PropertyNote.company_id == company.id,
            PropertyNote.property_id == property_item.id,
            PropertyNote.archived_at.is_(None),
        )
        .order_by(PropertyNote.created_at.asc())
        .all()
    )
    return [property_note_response(note) for note in notes]
