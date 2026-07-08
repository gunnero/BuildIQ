from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.common import IdMixin, TimestampMixin


class CalculationRun(IdMixin, TimestampMixin, Base):
    __tablename__ = "calculation_runs"

    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=True, index=True)
    project_task_id = Column(String(36), ForeignKey("project_tasks.id"), nullable=True, index=True)
    room_id = Column(String(36), ForeignKey("rooms.id"), nullable=True, index=True)
    measurement_set_id = Column(String(36), ForeignKey("measurement_sets.id"), nullable=True, index=True)
    engine_type = Column(String(50), nullable=False, index=True)
    engine_version = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False, default="draft", index=True)
    created_by_user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    archived_at = Column(DateTime(timezone=True), nullable=True)

    input = relationship(
        "CalculationInput",
        back_populates="calculation_run",
        uselist=False,
        cascade="all, delete-orphan",
    )
    output = relationship(
        "CalculationOutput",
        back_populates="calculation_run",
        uselist=False,
        cascade="all, delete-orphan",
    )
    line_items = relationship(
        "CalculationLineItem",
        back_populates="calculation_run",
        cascade="all, delete-orphan",
    )


class CalculationInput(IdMixin, Base):
    __tablename__ = "calculation_inputs"

    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    calculation_run_id = Column(
        String(36),
        ForeignKey("calculation_runs.id"),
        nullable=False,
        index=True,
    )
    payload = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)

    calculation_run = relationship("CalculationRun", back_populates="input")


class CalculationOutput(IdMixin, Base):
    __tablename__ = "calculation_outputs"

    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    calculation_run_id = Column(
        String(36),
        ForeignKey("calculation_runs.id"),
        nullable=False,
        index=True,
    )
    payload = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)

    calculation_run = relationship("CalculationRun", back_populates="output")


class CalculationLineItem(IdMixin, Base):
    __tablename__ = "calculation_line_items"

    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    calculation_run_id = Column(
        String(36),
        ForeignKey("calculation_runs.id"),
        nullable=False,
        index=True,
    )
    sort_order = Column(Integer, nullable=False, default=0)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    unit = Column(String(50), nullable=True)
    quantity = Column(Float, nullable=True)
    payload = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False)

    calculation_run = relationship("CalculationRun", back_populates="line_items")
