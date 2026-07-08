from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_company, get_current_user
from app.db.session import get_db
from app.models.customer import Customer, CustomerContact
from app.models.identity import Company, User
from app.models.kernel import AuditLog
from app.schemas.customer import (
    CustomerContactCreate,
    CustomerContactResponse,
    CustomerCreate,
    CustomerResponse,
    CustomerUpdate,
)
from app.services.customers import archive_customer, get_active_customer_for_company

router = APIRouter(prefix="/customers", tags=["customers"])


def customer_response(customer: Customer) -> CustomerResponse:
    return CustomerResponse(
        id=customer.id,
        company_id=customer.company_id,
        name=customer.name,
        phone=customer.phone,
        email=customer.email,
        address=customer.address,
        note=customer.note,
        status=customer.status,
        archived_at=customer.archived_at,
    )


def customer_contact_response(contact: CustomerContact) -> CustomerContactResponse:
    return CustomerContactResponse(
        id=contact.id,
        company_id=contact.company_id,
        customer_id=contact.customer_id,
        full_name=contact.full_name,
        phone=contact.phone,
        email=contact.email,
        role=contact.role,
        note=contact.note,
        is_primary=contact.is_primary,
        archived_at=contact.archived_at,
    )


@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(
    payload: CustomerCreate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> CustomerResponse:
    customer = Customer(company_id=company.id, **payload.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer_response(customer)


@router.get("", response_model=list[CustomerResponse])
def list_customers(
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> list[CustomerResponse]:
    customers = (
        db.query(Customer)
        .filter(Customer.company_id == company.id, Customer.archived_at.is_(None))
        .order_by(Customer.created_at.asc())
        .all()
    )
    return [customer_response(customer) for customer in customers]


@router.get("/{customer_id}", response_model=CustomerResponse)
def read_customer(
    customer_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> CustomerResponse:
    customer = get_active_customer_for_company(db, company_id=company.id, customer_id=customer_id)
    return customer_response(customer)


@router.patch("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: str,
    payload: CustomerUpdate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> CustomerResponse:
    customer = get_active_customer_for_company(db, company_id=company.id, customer_id=customer_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer_response(customer)


@router.post("/{customer_id}/archive", response_model=CustomerResponse)
def archive_customer_endpoint(
    customer_id: str,
    company: Company = Depends(get_current_company),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CustomerResponse:
    customer = get_active_customer_for_company(db, company_id=company.id, customer_id=customer_id)
    archive_customer(customer)
    db.add(
        AuditLog(
            company_id=company.id,
            acting_user_id=current_user.id,
            entity_type="customer",
            entity_id=customer.id,
            action="archived",
        )
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer_response(customer)


@router.post(
    "/{customer_id}/contacts",
    response_model=CustomerContactResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_customer_contact(
    customer_id: str,
    payload: CustomerContactCreate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> CustomerContactResponse:
    customer = get_active_customer_for_company(db, company_id=company.id, customer_id=customer_id)
    contact = CustomerContact(
        company_id=company.id,
        customer_id=customer.id,
        **payload.model_dump(),
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return customer_contact_response(contact)


@router.get("/{customer_id}/contacts", response_model=list[CustomerContactResponse])
def list_customer_contacts(
    customer_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> list[CustomerContactResponse]:
    customer = get_active_customer_for_company(db, company_id=company.id, customer_id=customer_id)
    contacts = (
        db.query(CustomerContact)
        .filter(
            CustomerContact.company_id == company.id,
            CustomerContact.customer_id == customer.id,
            CustomerContact.archived_at.is_(None),
        )
        .order_by(CustomerContact.created_at.asc())
        .all()
    )
    return [customer_contact_response(contact) for contact in contacts]
