from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.customer import Customer, Property


def not_found(message: str = "Записот не е пронајден.") -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)


def get_active_customer_for_company(
    db: Session,
    *,
    company_id: str,
    customer_id: str,
) -> Customer:
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
        raise not_found()
    return customer


def get_active_property_for_company(
    db: Session,
    *,
    company_id: str,
    property_id: str,
) -> Property:
    property_item = (
        db.query(Property)
        .filter(
            Property.id == property_id,
            Property.company_id == company_id,
            Property.archived_at.is_(None),
        )
        .one_or_none()
    )
    if property_item is None:
        raise not_found()
    return property_item


def archive_customer(customer: Customer) -> Customer:
    customer.status = "archived"
    customer.archived_at = datetime.utcnow()
    return customer


def archive_property(property_item: Property) -> Property:
    property_item.status = "archived"
    property_item.archived_at = datetime.utcnow()
    return property_item
