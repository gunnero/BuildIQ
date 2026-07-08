from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.common import IdMixin, TimestampMixin


class Room(IdMixin, TimestampMixin, Base):
    __tablename__ = "rooms"

    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    project_task_id = Column(String(36), ForeignKey("project_tasks.id"), nullable=True, index=True)
    name = Column(String(255), nullable=False)
    room_type = Column(String(50), nullable=False, default="room")
    floor = Column(String(100), nullable=True)
    note = Column(Text, nullable=True)
    length = Column(Float, nullable=False)
    width = Column(Float, nullable=False)
    height = Column(Float, nullable=False)
    archived_at = Column(DateTime(timezone=True), nullable=True)

    project = relationship("Project", back_populates="rooms")
    project_task = relationship("ProjectTask", back_populates="rooms")
    openings = relationship("RoomOpening", back_populates="room")


class RoomOpening(IdMixin, TimestampMixin, Base):
    __tablename__ = "room_openings"

    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    room_id = Column(String(36), ForeignKey("rooms.id"), nullable=False, index=True)
    opening_type = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False)
    width = Column(Float, nullable=False)
    height = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    note = Column(Text, nullable=True)
    archived_at = Column(DateTime(timezone=True), nullable=True)

    room = relationship("Room", back_populates="openings")


class MeasurementSet(IdMixin, TimestampMixin, Base):
    __tablename__ = "measurement_sets"

    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    project_task_id = Column(String(36), ForeignKey("project_tasks.id"), nullable=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    archived_at = Column(DateTime(timezone=True), nullable=True)

    project = relationship("Project", back_populates="measurement_sets")
    project_task = relationship("ProjectTask", back_populates="measurement_sets")
    items = relationship("MeasurementItem", back_populates="measurement_set")


class MeasurementItem(IdMixin, TimestampMixin, Base):
    __tablename__ = "measurement_items"

    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    measurement_set_id = Column(String(36), ForeignKey("measurement_sets.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    unit = Column(String(50), nullable=False)
    quantity = Column(Float, nullable=False)
    note = Column(Text, nullable=True)
    archived_at = Column(DateTime(timezone=True), nullable=True)

    measurement_set = relationship("MeasurementSet", back_populates="items")
