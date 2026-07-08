from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.common import IdMixin, TimestampMixin


class Payment(IdMixin, TimestampMixin, Base):
    __tablename__ = "payments"

    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    estimate_id = Column(String(36), ForeignKey("estimates.id"), nullable=True, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False, default="MKD")
    payment_method = Column(String(50), nullable=False)
    payment_date = Column(Date, nullable=False)
    status = Column(String(50), nullable=False, default="received", index=True)
    note = Column(Text, nullable=True)
    created_by_user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    reversal_reason = Column(Text, nullable=True)
    reversed_at = Column(DateTime(timezone=True), nullable=True)
    reversed_by_user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    archived_at = Column(DateTime(timezone=True), nullable=True)

    customer = relationship("Customer")
    project = relationship("Project")
    estimate = relationship("Estimate")
    created_by_user = relationship("User", foreign_keys=[created_by_user_id])
    reversed_by_user = relationship("User", foreign_keys=[reversed_by_user_id])
    allocations = relationship("PaymentAllocation", back_populates="payment")


class PaymentAllocation(IdMixin, TimestampMixin, Base):
    __tablename__ = "payment_allocations"

    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    payment_id = Column(String(36), ForeignKey("payments.id"), nullable=False, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=True, index=True)
    estimate_id = Column(String(36), ForeignKey("estimates.id"), nullable=True, index=True)
    amount = Column(Float, nullable=False)
    note = Column(Text, nullable=True)
    archived_at = Column(DateTime(timezone=True), nullable=True)

    payment = relationship("Payment", back_populates="allocations")
    project = relationship("Project")
    estimate = relationship("Estimate")


class ExpenseCategory(IdMixin, TimestampMixin, Base):
    __tablename__ = "expense_categories"

    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    archived_at = Column(DateTime(timezone=True), nullable=True)

    expenses = relationship("Expense", back_populates="category")


class Expense(IdMixin, TimestampMixin, Base):
    __tablename__ = "expenses"

    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=True, index=True)
    category_id = Column(String(36), ForeignKey("expense_categories.id"), nullable=True, index=True)
    supplier_id = Column(String(36), ForeignKey("suppliers.id"), nullable=True, index=True)
    material_id = Column(String(36), ForeignKey("materials.id"), nullable=True, index=True)
    description = Column(Text, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False, default="MKD")
    expense_date = Column(Date, nullable=False)
    payment_method = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, default="recorded", index=True)
    note = Column(Text, nullable=True)
    created_by_user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    reversal_reason = Column(Text, nullable=True)
    reversed_at = Column(DateTime(timezone=True), nullable=True)
    reversed_by_user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    archived_at = Column(DateTime(timezone=True), nullable=True)

    project = relationship("Project")
    category = relationship("ExpenseCategory", back_populates="expenses")
    supplier = relationship("Supplier")
    material = relationship("Material")
    created_by_user = relationship("User", foreign_keys=[created_by_user_id])
    reversed_by_user = relationship("User", foreign_keys=[reversed_by_user_id])
