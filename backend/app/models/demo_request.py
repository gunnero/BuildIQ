from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String

from app.db.base import Base
from app.models.common import IdMixin, TimestampMixin


class DemoRequest(IdMixin, TimestampMixin, Base):
    __tablename__ = "demo_requests"
    __table_args__ = (Index("ix_demo_requests_ip_created", "source_key", "created_at"),)

    name = Column(String(120), nullable=False)
    email = Column(String(254), nullable=False, unique=True)
    company_name = Column(String(120), nullable=False)
    message = Column(String(1000), nullable=False)
    source_key = Column(String(64), nullable=False)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approved_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, unique=True)
    activated_at = Column(DateTime(timezone=True), nullable=True)
    notified_at = Column(DateTime(timezone=True), nullable=True)
    invitation_sent_at = Column(DateTime(timezone=True), nullable=True)
    email_attempts = Column(Integer, nullable=False, default=0)
    next_email_at = Column(DateTime(timezone=True), nullable=True, index=True)
