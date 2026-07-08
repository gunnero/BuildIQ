from sqlalchemy import Column, Date, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.common import IdMixin, TimestampMixin


class Project(IdMixin, TimestampMixin, Base):
    __tablename__ = "projects"

    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False, index=True)
    property_id = Column(String(36), ForeignKey("properties.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    address = Column(String(500), nullable=True)
    status = Column(String(50), nullable=False, default="draft")
    start_date = Column(Date, nullable=True)
    due_date = Column(Date, nullable=True)
    archived_at = Column(DateTime(timezone=True), nullable=True)

    company = relationship("Company", back_populates="projects")
    customer = relationship("Customer", back_populates="projects")
    property = relationship("Property", back_populates="projects")
    tasks = relationship("ProjectTask", back_populates="project")
    status_history = relationship("ProjectStatusHistory", back_populates="project")
    timeline_events = relationship("ProjectTimelineEvent", back_populates="project")


class ProjectTask(IdMixin, TimestampMixin, Base):
    __tablename__ = "project_tasks"

    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="draft")
    assigned_user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    due_date = Column(Date, nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    archived_at = Column(DateTime(timezone=True), nullable=True)

    project = relationship("Project", back_populates="tasks")
    assigned_user = relationship("User")


class ProjectStatusHistory(IdMixin, Base):
    __tablename__ = "project_status_history"

    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    from_status = Column(String(50), nullable=True)
    to_status = Column(String(50), nullable=False)
    note = Column(Text, nullable=True)
    changed_by_user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False)

    project = relationship("Project", back_populates="status_history")
    changed_by_user = relationship("User")


class ProjectTimelineEvent(IdMixin, Base):
    __tablename__ = "project_timeline_events"

    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    event_type = Column(String(100), nullable=False)
    message = Column(Text, nullable=True)
    created_by_user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False)

    project = relationship("Project", back_populates="timeline_events")
    created_by_user = relationship("User")
