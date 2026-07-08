from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, JSON, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.common import IdMixin, TimestampMixin


class Supplier(IdMixin, TimestampMixin, Base):
    __tablename__ = "suppliers"

    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    parent_supplier_id = Column(String(36), ForeignKey("suppliers.id"), nullable=True, index=True)
    name = Column(String(255), nullable=False)
    supplier_type = Column(String(50), nullable=False, default="supplier")
    tax_number = Column(String(64), nullable=True)
    phone = Column(String(64), nullable=True)
    email = Column(String(255), nullable=True)
    address = Column(String(500), nullable=True)
    note = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="active")
    archived_at = Column(DateTime(timezone=True), nullable=True)

    contacts = relationship("SupplierContact", back_populates="supplier")
    agreements = relationship("SupplierAgreement", back_populates="supplier")
    price_books = relationship("PriceBook", back_populates="supplier")


class SupplierContact(IdMixin, TimestampMixin, Base):
    __tablename__ = "supplier_contacts"

    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    supplier_id = Column(String(36), ForeignKey("suppliers.id"), nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(64), nullable=True)
    email = Column(String(255), nullable=True)
    role = Column(String(100), nullable=True)
    note = Column(Text, nullable=True)
    is_primary = Column(Boolean, nullable=False, default=False)
    archived_at = Column(DateTime(timezone=True), nullable=True)

    supplier = relationship("Supplier", back_populates="contacts")


class SupplierAgreement(IdMixin, TimestampMixin, Base):
    __tablename__ = "supplier_agreements"

    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    supplier_id = Column(String(36), ForeignKey("suppliers.id"), nullable=False, index=True)
    agreement_number = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False, default="draft")
    starts_on = Column(Date, nullable=True)
    ends_on = Column(Date, nullable=True)
    terms_snapshot = Column(JSON, nullable=False, default=dict)
    notes = Column(Text, nullable=True)
    archived_at = Column(DateTime(timezone=True), nullable=True)

    supplier = relationship("Supplier", back_populates="agreements")
    price_books = relationship("PriceBook", back_populates="supplier_agreement")


class PriceBook(IdMixin, TimestampMixin, Base):
    __tablename__ = "price_books"

    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    supplier_id = Column(String(36), ForeignKey("suppliers.id"), nullable=True, index=True)
    supplier_agreement_id = Column(
        String(36),
        ForeignKey("supplier_agreements.id"),
        nullable=True,
        index=True,
    )
    name = Column(String(255), nullable=False)
    price_type = Column(String(50), nullable=False, default="retail", index=True)
    status = Column(String(50), nullable=False, default="active", index=True)
    currency = Column(String(3), nullable=False, default="MKD")
    valid_from = Column(Date, nullable=False)
    valid_until = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    archived_at = Column(DateTime(timezone=True), nullable=True)

    supplier = relationship("Supplier", back_populates="price_books")
    supplier_agreement = relationship("SupplierAgreement", back_populates="price_books")
    items = relationship("PriceBookItem", back_populates="price_book")


class PriceBookItem(IdMixin, TimestampMixin, Base):
    __tablename__ = "price_book_items"

    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    price_book_id = Column(String(36), ForeignKey("price_books.id"), nullable=False, index=True)
    material_id = Column(String(36), ForeignKey("materials.id"), nullable=False, index=True)
    supplier_id = Column(String(36), ForeignKey("suppliers.id"), nullable=True, index=True)
    supplier_sku = Column(String(100), nullable=True)
    unit_price = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False, default="MKD")
    valid_from = Column(Date, nullable=False)
    valid_until = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    archived_at = Column(DateTime(timezone=True), nullable=True)

    price_book = relationship("PriceBook", back_populates="items")
    material = relationship("Material")
    supplier = relationship("Supplier")


class ProjectMaterialPriceOverride(IdMixin, TimestampMixin, Base):
    __tablename__ = "project_material_price_overrides"

    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    material_id = Column(String(36), ForeignKey("materials.id"), nullable=False, index=True)
    supplier_id = Column(String(36), ForeignKey("suppliers.id"), nullable=True, index=True)
    unit_price = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False, default="MKD")
    valid_from = Column(Date, nullable=False)
    valid_until = Column(Date, nullable=True)
    reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_by_user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    archived_at = Column(DateTime(timezone=True), nullable=True)

    project = relationship("Project")
    material = relationship("Material")
    supplier = relationship("Supplier")
    created_by_user = relationship("User")
