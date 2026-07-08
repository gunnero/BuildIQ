from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.common import IdMixin, TimestampMixin


class MaterialCategory(IdMixin, TimestampMixin, Base):
    __tablename__ = "material_categories"

    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    archived_at = Column(DateTime(timezone=True), nullable=True)

    materials = relationship("Material", back_populates="category")


class MaterialManufacturer(IdMixin, TimestampMixin, Base):
    __tablename__ = "material_manufacturers"

    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    website = Column(String(500), nullable=True)
    note = Column(Text, nullable=True)
    archived_at = Column(DateTime(timezone=True), nullable=True)

    materials = relationship("Material", back_populates="manufacturer")


class MaterialUnit(IdMixin, TimestampMixin, Base):
    __tablename__ = "material_units"

    company_id = Column(String(36), ForeignKey("companies.id"), nullable=True, index=True)
    key = Column(String(50), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_default = Column(Boolean, nullable=False, default=False)
    archived_at = Column(DateTime(timezone=True), nullable=True)

    materials = relationship("Material", back_populates="unit")


class Material(IdMixin, TimestampMixin, Base):
    __tablename__ = "materials"

    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    sku = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    category_id = Column(String(36), ForeignKey("material_categories.id"), nullable=True, index=True)
    manufacturer_id = Column(String(36), ForeignKey("material_manufacturers.id"), nullable=True, index=True)
    unit_id = Column(String(36), ForeignKey("material_units.id"), nullable=False, index=True)
    coverage_value = Column(Float, nullable=True)
    coverage_unit = Column(String(50), nullable=True)
    package_quantity = Column(Float, nullable=True)
    waste_percentage_default = Column(Float, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    archived_at = Column(DateTime(timezone=True), nullable=True)

    category = relationship("MaterialCategory", back_populates="materials")
    manufacturer = relationship("MaterialManufacturer", back_populates="materials")
    unit = relationship("MaterialUnit", back_populates="materials")
    consumption_rules = relationship("MaterialConsumptionRule", back_populates="material")


class MaterialConsumptionRule(IdMixin, TimestampMixin, Base):
    __tablename__ = "material_consumption_rules"

    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    material_id = Column(String(36), ForeignKey("materials.id"), nullable=False, index=True)
    engine_type = Column(String(50), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    input_unit = Column(String(50), nullable=True)
    consumption_rate = Column(Float, nullable=True)
    waste_percentage = Column(Float, nullable=True)
    description = Column(Text, nullable=True)
    archived_at = Column(DateTime(timezone=True), nullable=True)

    material = relationship("Material", back_populates="consumption_rules")
