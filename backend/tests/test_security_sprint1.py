from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.identity import Role, User, UserRole
from app.models.subscription import Subscription


def login(client: TestClient, email: str, password: str) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def create_role_user(
    db_session: Session,
    seeded_identity: dict[str, str],
    *,
    role_key: str,
    email: str,
) -> str:
    user = User(
        company_id=seeded_identity["demo_company_id"],
        name=role_key.title(),
        email=email,
        password_hash=hash_password("role-user-password"),
        status="active",
    )
    role = (
        db_session.query(Role)
        .filter(
            Role.company_id == seeded_identity["demo_company_id"],
            Role.key == role_key,
        )
        .one_or_none()
    )
    if role is None:
        role = Role(
            company_id=seeded_identity["demo_company_id"],
            key=role_key,
            name=role_key.title(),
            is_system_role=True,
        )
        db_session.add(role)
    db_session.add(user)
    db_session.flush()
    db_session.add(UserRole(user_id=user.id, role_id=role.id))
    db_session.commit()
    return user.email


def test_zero_role_user_cannot_mutate_customer(
    client: TestClient,
    db_session: Session,
    seeded_identity: dict[str, str],
) -> None:
    email = create_role_user(
        db_session,
        seeded_identity,
        role_key="zero-role",
        email="zero-role@demo.buildiq.test",
    )
    headers = login(client, email, "role-user-password")

    response = client.post(
        "/api/v1/customers",
        json={"name": "Blocked", "email": "blocked@example.test"},
        headers=headers,
    )

    assert response.status_code == 403


def test_worker_cannot_reverse_financial_records_or_change_pricing(
    client: TestClient,
    db_session: Session,
    seeded_identity: dict[str, str],
) -> None:
    email = create_role_user(
        db_session,
        seeded_identity,
        role_key="worker",
        email="worker@demo.buildiq.test",
    )
    headers = login(client, email, "role-user-password")

    assert client.post(
        "/api/v1/payments/missing/reverse",
        json={"reason": "blocked"},
        headers=headers,
    ).status_code == 403
    assert client.patch(
        "/api/v1/price-book-items/missing",
        json={"unit_price": 99},
        headers=headers,
    ).status_code == 403
    assert client.post(
        "/api/v1/projects/missing/archive",
        headers=headers,
    ).status_code == 403
    assert client.post(
        "/api/v1/tasks/missing/archive",
        headers=headers,
    ).status_code == 403


def test_accountant_cannot_mutate_measurements_or_procurement(
    client: TestClient,
    db_session: Session,
    seeded_identity: dict[str, str],
) -> None:
    email = create_role_user(
        db_session,
        seeded_identity,
        role_key="accountant",
        email="accountant@demo.buildiq.test",
    )
    headers = login(client, email, "role-user-password")

    assert client.patch(
        "/api/v1/measurement-items/missing",
        json={"quantity": 2},
        headers=headers,
    ).status_code == 403
    assert client.patch(
        "/api/v1/suppliers/missing",
        json={"name": "Blocked"},
        headers=headers,
    ).status_code == 403


def test_suspended_and_cancelled_subscriptions_block_business_access(
    client: TestClient,
    db_session: Session,
    seeded_identity: dict[str, str],
) -> None:
    headers = login(
        client,
        seeded_identity["owner_email"],
        seeded_identity["owner_password"],
    )
    subscription = db_session.get(Subscription, seeded_identity["subscription_id"])
    assert subscription is not None

    for blocked_status in ("suspended", "cancelled"):
        subscription.status = blocked_status
        db_session.commit()
        assert client.get("/api/v1/customers", headers=headers).status_code == 403
        assert client.get("/api/v1/companies/me", headers=headers).status_code == 200
        assert client.get("/api/v1/subscription/me", headers=headers).status_code == 200

        subscription.status = "active"
        db_session.commit()
