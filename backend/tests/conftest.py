import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.identity import (
    Company,
    Permission,
    Role,
    RolePermission,
    User,
    UserRole,
)
from app.models.subscription import Subscription, SubscriptionPlan


@pytest.fixture()
def db_session() -> Session:
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(bind=engine)
    session = testing_session_local()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def seeded_identity(db_session: Session) -> dict[str, str]:
    demo_company = Company(name="Demo Build Company", status="active")
    other_company = Company(name="Other Build Company", status="active")
    db_session.add_all([demo_company, other_company])
    db_session.flush()

    owner_user = User(
        company_id=demo_company.id,
        name="Demo Owner",
        email="owner@demo.buildiq.test",
        password_hash=hash_password("correct-password"),
        status="active",
    )
    other_user = User(
        company_id=other_company.id,
        name="Other Owner",
        email="owner@other.buildiq.test",
        password_hash=hash_password("other-password"),
        status="active",
    )
    db_session.add_all([owner_user, other_user])
    db_session.flush()

    owner_role = Role(
        company_id=demo_company.id,
        key="owner",
        name="Owner",
        is_system_role=True,
    )
    manager_role = Role(
        company_id=demo_company.id,
        key="manager",
        name="Manager",
        is_system_role=True,
    )
    worker_role = Role(
        company_id=demo_company.id,
        key="worker",
        name="Worker",
        is_system_role=True,
    )
    view_subscription = Permission(
        key="subscription:view",
        name="View subscription",
    )
    db_session.add_all([owner_role, manager_role, worker_role, view_subscription])
    db_session.flush()
    db_session.add_all(
        [
            UserRole(user_id=owner_user.id, role_id=owner_role.id),
            RolePermission(role_id=owner_role.id, permission_id=view_subscription.id),
        ]
    )

    plan = SubscriptionPlan(
        key="starter",
        name="Starter",
        price_mkd=0,
        billing_period="monthly",
        is_active=True,
    )
    db_session.add(plan)
    db_session.flush()
    subscription = Subscription(
        company_id=demo_company.id,
        plan_id=plan.id,
        status="active",
    )
    db_session.add(subscription)
    db_session.commit()

    return {
        "demo_company_id": demo_company.id,
        "other_company_id": other_company.id,
        "owner_user_id": owner_user.id,
        "owner_email": owner_user.email,
        "owner_password": "correct-password",
        "subscription_id": subscription.id,
    }


@pytest.fixture()
def client(db_session: Session, seeded_identity: dict[str, str]) -> TestClient:
    def override_get_db() -> Session:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
