from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.common import IdMixin, TimestampMixin


class SubscriptionPlan(IdMixin, TimestampMixin, Base):
    __tablename__ = "subscription_plans"

    key = Column(String(100), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    price_mkd = Column(Integer, nullable=False, default=0)
    billing_period = Column(String(50), nullable=False, default="monthly")
    is_active = Column(Boolean, nullable=False, default=True)

    subscriptions = relationship("Subscription", back_populates="plan")


class Subscription(IdMixin, TimestampMixin, Base):
    __tablename__ = "subscriptions"

    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    plan_id = Column(String(36), ForeignKey("subscription_plans.id"), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="trialing")
    starts_on = Column(Date, nullable=True)
    ends_on = Column(Date, nullable=True)
    trial_ends_on = Column(Date, nullable=True)

    company = relationship("Company", back_populates="subscriptions")
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")
