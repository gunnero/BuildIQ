from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.common import IdMixin, TimestampMixin


class Customer(IdMixin, TimestampMixin, Base):
    __tablename__ = "customers"

    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(64), nullable=True)
    email = Column(String(255), nullable=True)
    address = Column(String(500), nullable=True)
    note = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="active")
    archived_at = Column(DateTime(timezone=True), nullable=True)

    company = relationship("Company", back_populates="customers")
    contacts = relationship(
        "CustomerContact",
        back_populates="customer",
        cascade="all, delete-orphan",
    )
    properties = relationship("Property", back_populates="customer")


class CustomerContact(IdMixin, TimestampMixin, Base):
    __tablename__ = "customer_contacts"

    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(64), nullable=True)
    email = Column(String(255), nullable=True)
    role = Column(String(100), nullable=True)
    note = Column(Text, nullable=True)
    is_primary = Column(Boolean, nullable=False, default=False)
    archived_at = Column(DateTime(timezone=True), nullable=True)

    customer = relationship("Customer", back_populates="contacts")


class Property(IdMixin, TimestampMixin, Base):
    __tablename__ = "properties"

    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    address = Column(String(500), nullable=True)
    city = Column(String(255), nullable=True)
    note = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="active")
    archived_at = Column(DateTime(timezone=True), nullable=True)

    company = relationship("Company", back_populates="properties")
    customer = relationship("Customer", back_populates="properties")
    contacts = relationship(
        "PropertyContact",
        back_populates="property",
        cascade="all, delete-orphan",
    )
    notes = relationship(
        "PropertyNote",
        back_populates="property",
        cascade="all, delete-orphan",
    )


class PropertyContact(IdMixin, TimestampMixin, Base):
    __tablename__ = "property_contacts"

    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    property_id = Column(String(36), ForeignKey("properties.id"), nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(64), nullable=True)
    email = Column(String(255), nullable=True)
    role = Column(String(100), nullable=True)
    note = Column(Text, nullable=True)
    is_primary = Column(Boolean, nullable=False, default=False)
    archived_at = Column(DateTime(timezone=True), nullable=True)

    property = relationship("Property", back_populates="contacts")


class PropertyNote(IdMixin, TimestampMixin, Base):
    __tablename__ = "property_notes"

    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    property_id = Column(String(36), ForeignKey("properties.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_by_user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    archived_at = Column(DateTime(timezone=True), nullable=True)

    property = relationship("Property", back_populates="notes")
