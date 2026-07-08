from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.identity import User


def auth_headers(client: TestClient, email: str, password: str) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_login_succeeds_with_valid_credentials(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": seeded_identity["owner_email"],
            "password": seeded_identity["owner_password"],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str)
    assert body["access_token"]


def test_login_fails_with_invalid_credentials(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": seeded_identity["owner_email"],
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401


def test_auth_me_requires_authentication(client: TestClient) -> None:
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401


def test_auth_me_returns_current_user(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = auth_headers(
        client,
        seeded_identity["owner_email"],
        seeded_identity["owner_password"],
    )

    response = client.get("/api/v1/auth/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["id"] == seeded_identity["owner_user_id"]
    assert response.json()["company_id"] == seeded_identity["demo_company_id"]


def test_password_hashes_are_not_plain_text(
    db_session: Session,
    seeded_identity: dict[str, str],
) -> None:
    password = "correct-password"
    hashed_password = hash_password(password)

    assert hashed_password != password
    assert verify_password(password, hashed_password)

    user = db_session.query(User).filter(User.email == "owner@demo.buildiq.test").one()
    assert user.password_hash != password
    assert verify_password(password, user.password_hash)
