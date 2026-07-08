from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.common import IdMixin, TimestampMixin


class Company(IdMixin, TimestampMixin, Base):
    __tablename__ = "companies"

    name = Column(String(255), nullable=False)
    tax_number = Column(String(64), nullable=True)
    address = Column(String(500), nullable=True)
    phone = Column(String(64), nullable=True)
    email = Column(String(255), nullable=True)
    status = Column(String(50), nullable=False, default="active")
    is_internal = Column(Boolean, nullable=False, default=False)

    users = relationship("User", back_populates="company")
    roles = relationship("Role", back_populates="company")
    subscriptions = relationship("Subscription", back_populates="company")
    customers = relationship("Customer", back_populates="company")
    properties = relationship("Property", back_populates="company")
    projects = relationship("Project", back_populates="company")


class User(IdMixin, TimestampMixin, Base):
    __tablename__ = "users"

    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(512), nullable=False)
    status = Column(String(50), nullable=False, default="active")
    is_hq_admin = Column(Boolean, nullable=False, default=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    company = relationship("Company", back_populates="users")
    user_roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")


class Role(IdMixin, TimestampMixin, Base):
    __tablename__ = "roles"
    __table_args__ = (UniqueConstraint("company_id", "key", name="uq_roles_company_key"),)

    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    key = Column(String(100), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    is_system_role = Column(Boolean, nullable=False, default=False)

    company = relationship("Company", back_populates="roles")
    user_roles = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")
    role_permissions = relationship(
        "RolePermission",
        back_populates="role",
        cascade="all, delete-orphan",
    )


class Permission(IdMixin, Base):
    __tablename__ = "permissions"

    key = Column(String(150), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)

    role_permissions = relationship(
        "RolePermission",
        back_populates="permission",
        cascade="all, delete-orphan",
    )


class UserRole(IdMixin, Base):
    __tablename__ = "user_roles"
    __table_args__ = (UniqueConstraint("user_id", "role_id", name="uq_user_roles_user_role"),)

    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    role_id = Column(String(36), ForeignKey("roles.id"), nullable=False, index=True)

    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")


class RolePermission(IdMixin, Base):
    __tablename__ = "role_permissions"
    __table_args__ = (
        UniqueConstraint(
            "role_id",
            "permission_id",
            name="uq_role_permissions_role_permission",
        ),
    )

    role_id = Column(String(36), ForeignKey("roles.id"), nullable=False, index=True)
    permission_id = Column(String(36), ForeignKey("permissions.id"), nullable=False, index=True)

    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission", back_populates="role_permissions")
