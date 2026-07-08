from fastapi.testclient import TestClient

from tests.test_auth import auth_headers


def test_companies_me_returns_only_current_company(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = auth_headers(
        client,
        seeded_identity["owner_email"],
        seeded_identity["owner_password"],
    )

    response = client.get("/api/v1/companies/me", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == seeded_identity["demo_company_id"]
    assert body["id"] != seeded_identity["other_company_id"]
    assert body["name"] == "Demo Build Company"


def test_subscription_endpoint_returns_current_company_subscription(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = auth_headers(
        client,
        seeded_identity["owner_email"],
        seeded_identity["owner_password"],
    )

    response = client.get("/api/v1/subscription/me", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == seeded_identity["subscription_id"]
    assert body["company_id"] == seeded_identity["demo_company_id"]
    assert body["status"] == "active"
    assert body["plan"]["key"] == "starter"
