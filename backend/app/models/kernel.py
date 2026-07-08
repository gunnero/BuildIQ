from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, JSON, String

from app.db.base import Base
from app.models.common import IdMixin, TimestampMixin


class FeatureFlag(IdMixin, TimestampMixin, Base):
    __tablename__ = "feature_flags"

    key = Column(String(150), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    default_enabled = Column(Boolean, nullable=False, default=False)


class AuditLog(IdMixin, Base):
    __tablename__ = "audit_logs"

    company_id = Column(String(36), ForeignKey("companies.id"), nullable=True, index=True)
    acting_user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    entity_type = Column(String(150), nullable=False)
    entity_id = Column(String(36), nullable=True)
    action = Column(String(150), nullable=False)
    before_snapshot = Column(JSON, nullable=True)
    after_snapshot = Column(JSON, nullable=True)
    ip_address = Column(String(64), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
