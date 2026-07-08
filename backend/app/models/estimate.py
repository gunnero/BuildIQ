from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.common import IdMixin, TimestampMixin


class Estimate(IdMixin, TimestampMixin, Base):
    __tablename__ = "estimates"

    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False, index=True)
    property_id = Column(String(36), ForeignKey("properties.id"), nullable=False, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    estimate_number = Column(String(100), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="draft", index=True)
    source_calculation_run_id = Column(
        String(36),
        ForeignKey("calculation_runs.id"),
        nullable=True,
        index=True,
    )
    sent_at = Column(DateTime(timezone=True), nullable=True)
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    rejected_at = Column(DateTime(timezone=True), nullable=True)
    archived_at = Column(DateTime(timezone=True), nullable=True)

    customer = relationship("Customer")
    property = relationship("Property")
    project = relationship("Project")
    source_calculation_run = relationship("CalculationRun")
    revisions = relationship("EstimateRevision", back_populates="estimate")


class EstimateRevision(IdMixin, TimestampMixin, Base):
    __tablename__ = "estimate_revisions"

    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    estimate_id = Column(String(36), ForeignKey("estimates.id"), nullable=False, index=True)
    revision_number = Column(Integer, nullable=False)
    status = Column(String(50), nullable=False, default="draft", index=True)
    notes = Column(Text, nullable=True)
    terms = Column(Text, nullable=True)
    source_calculation_run_id = Column(
        String(36),
        ForeignKey("calculation_runs.id"),
        nullable=True,
        index=True,
    )
    sent_at = Column(DateTime(timezone=True), nullable=True)
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    rejected_at = Column(DateTime(timezone=True), nullable=True)
    archived_at = Column(DateTime(timezone=True), nullable=True)

    estimate = relationship("Estimate", back_populates="revisions")
    source_calculation_run = relationship("CalculationRun")
    items = relationship("EstimateItem", back_populates="revision")


class EstimateItem(IdMixin, TimestampMixin, Base):
    __tablename__ = "estimate_items"

    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    estimate_revision_id = Column(
        String(36),
        ForeignKey("estimate_revisions.id"),
        nullable=False,
        index=True,
    )
    item_type = Column(String(50), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    material_id = Column(String(36), ForeignKey("materials.id"), nullable=True, index=True)
    quantity = Column(Float, nullable=False, default=1.0)
    unit = Column(String(50), nullable=True)
    unit_price = Column(Float, nullable=False, default=0.0)
    total_price = Column(Float, nullable=False, default=0.0)
    source_calculation_run_id = Column(
        String(36),
        ForeignKey("calculation_runs.id"),
        nullable=True,
        index=True,
    )
    source_calculation_line_item_id = Column(
        String(36),
        ForeignKey("calculation_line_items.id"),
        nullable=True,
        index=True,
    )
    sort_order = Column(Integer, nullable=False, default=0)
    archived_at = Column(DateTime(timezone=True), nullable=True)

    revision = relationship("EstimateRevision", back_populates="items")
    material = relationship("Material")
    source_calculation_run = relationship("CalculationRun")
    source_calculation_line_item = relationship("CalculationLineItem")


class EstimateDocument(IdMixin, TimestampMixin, Base):
    __tablename__ = "estimate_documents"

    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    estimate_id = Column(String(36), ForeignKey("estimates.id"), nullable=False, index=True)
    revision_id = Column(String(36), ForeignKey("estimate_revisions.id"), nullable=False, index=True)
    document_type = Column(String(100), nullable=False, index=True)
    file_path = Column(String(1000), nullable=False)
    generated_by_user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    generated_at = Column(DateTime(timezone=True), nullable=False)
    archived_at = Column(DateTime(timezone=True), nullable=True)

    estimate = relationship("Estimate")
    revision = relationship("EstimateRevision")
    generated_by_user = relationship("User")
