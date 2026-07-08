import os

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.identity import Company, Permission, Role, RolePermission, User, UserRole
from app.models.kernel import AuditLog, FeatureFlag
from app.models.subscription import Subscription, SubscriptionPlan

HQ_EMAIL = "hq@buildiq.local"
OWNER_EMAIL = "owner@demo.buildiq.local"
DEFAULT_PASSWORD = "ChangeMe123!"


def get_or_create_company(
    db: Session,
    name: str,
    *,
    is_internal: bool = False,
) -> Company:
    company = db.query(Company).filter(Company.name == name).one_or_none()
    if company is not None:
        return company

    company = Company(name=name, status="active", is_internal=is_internal)
    db.add(company)
    db.flush()
    return company


def get_or_create_user(
    db: Session,
    *,
    company_id: str,
    name: str,
    email: str,
    password: str,
    is_hq_admin: bool = False,
) -> User:
    user = db.query(User).filter(User.email == email).one_or_none()
    if user is not None:
        return user

    user = User(
        company_id=company_id,
        name=name,
        email=email,
        password_hash=hash_password(password),
        status="active",
        is_hq_admin=is_hq_admin,
    )
    db.add(user)
    db.flush()
    return user


def get_or_create_permission(db: Session, key: str, name: str) -> Permission:
    permission = db.query(Permission).filter(Permission.key == key).one_or_none()
    if permission is not None:
        return permission

    permission = Permission(key=key, name=name)
    db.add(permission)
    db.flush()
    return permission


def get_or_create_role(
    db: Session,
    *,
    company_id: str,
    key: str,
    name: str,
) -> Role:
    role = (
        db.query(Role)
        .filter(Role.company_id == company_id, Role.key == key)
        .one_or_none()
    )
    if role is not None:
        return role

    role = Role(company_id=company_id, key=key, name=name, is_system_role=True)
    db.add(role)
    db.flush()
    return role


def ensure_user_role(db: Session, user: User, role: Role) -> None:
    exists = (
        db.query(UserRole)
        .filter(UserRole.user_id == user.id, UserRole.role_id == role.id)
        .one_or_none()
    )
    if exists is None:
        db.add(UserRole(user_id=user.id, role_id=role.id))


def ensure_role_permission(db: Session, role: Role, permission: Permission) -> None:
    exists = (
        db.query(RolePermission)
        .filter(
            RolePermission.role_id == role.id,
            RolePermission.permission_id == permission.id,
        )
        .one_or_none()
    )
    if exists is None:
        db.add(RolePermission(role_id=role.id, permission_id=permission.id))


def get_or_create_plan(db: Session) -> SubscriptionPlan:
    plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.key == "starter").one_or_none()
    if plan is not None:
        return plan

    plan = SubscriptionPlan(
        key="starter",
        name="Starter",
        price_mkd=0,
        billing_period="monthly",
        is_active=True,
    )
    db.add(plan)
    db.flush()
    return plan


def ensure_subscription(db: Session, company: Company, plan: SubscriptionPlan) -> None:
    subscription = (
        db.query(Subscription)
        .filter(Subscription.company_id == company.id, Subscription.plan_id == plan.id)
        .one_or_none()
    )
    if subscription is None:
        db.add(Subscription(company_id=company.id, plan_id=plan.id, status="active"))


def ensure_feature_flag(db: Session) -> None:
    feature_flag = (
        db.query(FeatureFlag)
        .filter(FeatureFlag.key == "identity.tenant_foundation")
        .one_or_none()
    )
    if feature_flag is None:
        db.add(
            FeatureFlag(
                key="identity.tenant_foundation",
                name="Identity and Tenant Foundation",
                default_enabled=True,
            )
        )


def seed_development_data() -> None:
    hq_password = os.getenv("BUILDIQ_SEED_HQ_PASSWORD", DEFAULT_PASSWORD)
    owner_password = os.getenv("BUILDIQ_SEED_OWNER_PASSWORD", DEFAULT_PASSWORD)

    db = SessionLocal()
    try:
        hq_company = get_or_create_company(db, "BuildIQ HQ", is_internal=True)
        demo_company = get_or_create_company(db, "Demo Build Company")

        get_or_create_user(
            db,
            company_id=hq_company.id,
            name="BuildIQ HQ Admin",
            email=HQ_EMAIL,
            password=hq_password,
            is_hq_admin=True,
        )
        owner_user = get_or_create_user(
            db,
            company_id=demo_company.id,
            name="Demo Owner",
            email=OWNER_EMAIL,
            password=owner_password,
        )

        roles = {
            "owner": get_or_create_role(db, company_id=demo_company.id, key="owner", name="Owner"),
            "manager": get_or_create_role(db, company_id=demo_company.id, key="manager", name="Manager"),
            "worker": get_or_create_role(db, company_id=demo_company.id, key="worker", name="Worker"),
        }

        permissions = [
            get_or_create_permission(db, "company:read", "Read company"),
            get_or_create_permission(db, "subscription:read", "Read subscription"),
            get_or_create_permission(db, "users:manage", "Manage users"),
        ]
        for permission in permissions:
            ensure_role_permission(db, roles["owner"], permission)
        ensure_user_role(db, owner_user, roles["owner"])

        plan = get_or_create_plan(db)
        ensure_subscription(db, demo_company, plan)
        ensure_feature_flag(db)

        db.add(
            AuditLog(
                company_id=demo_company.id,
                acting_user_id=owner_user.id,
                entity_type="development_seed",
                entity_id=demo_company.id,
                action="seeded",
            )
        )
        db.commit()
    finally:
        db.close()

    print("Development seed data ready.")
    print(f"HQ admin: {HQ_EMAIL}")
    print(f"Demo owner: {OWNER_EMAIL}")


def main() -> None:
    seed_development_data()


if __name__ == "__main__":
    main()
