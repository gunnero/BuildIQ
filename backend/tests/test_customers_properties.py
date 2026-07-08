from collections.abc import Iterable
from typing import Optional

from fastapi.testclient import TestClient

from tests.test_auth import auth_headers


def owner_headers(client: TestClient, seeded_identity: dict[str, str]) -> dict[str, str]:
    return auth_headers(
        client,
        seeded_identity["owner_email"],
        seeded_identity["owner_password"],
    )


def other_headers(client: TestClient, seeded_identity: dict[str, str]) -> dict[str, str]:
    return auth_headers(
        client,
        seeded_identity["other_email"],
        seeded_identity["other_password"],
    )


def create_customer(
    client: TestClient,
    headers: dict[str, str],
    *,
    name: str = "Aleksandar Construction",
) -> dict[str, object]:
    response = client.post(
        "/api/v1/customers",
        json={
            "name": name,
            "phone": "+38970111222",
            "email": "customer@example.test",
            "address": "Partizanska 1",
            "note": "Initial customer note",
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def create_property(
    client: TestClient,
    headers: dict[str, str],
    customer_id: str,
    *,
    name: str = "Apartment Renovation Site",
) -> dict[str, object]:
    response = client.post(
        "/api/v1/properties",
        json={
            "customer_id": customer_id,
            "name": name,
            "address": "Ilindenska 10",
            "city": "Skopje",
            "note": "Property note",
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def test_customer_create_list_detail_update_archive(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)

    created = create_customer(client, headers)

    assert created["company_id"] == seeded_identity["demo_company_id"]
    assert created["name"] == "Aleksandar Construction"
    assert created["status"] == "active"
    assert created["archived_at"] is None

    list_response = client.get("/api/v1/customers", headers=headers)
    assert list_response.status_code == 200
    assert [customer["id"] for customer in list_response.json()] == [created["id"]]

    detail_response = client.get(f"/api/v1/customers/{created['id']}", headers=headers)
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == created["id"]

    update_response = client.patch(
        f"/api/v1/customers/{created['id']}",
        json={"name": "Aleksandar Renovations", "note": "Updated note"},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Aleksandar Renovations"
    assert update_response.json()["note"] == "Updated note"

    archive_response = client.post(f"/api/v1/customers/{created['id']}/archive", headers=headers)
    assert archive_response.status_code == 200
    assert archive_response.json()["status"] == "archived"
    assert archive_response.json()["archived_at"] is not None

    list_after_archive = client.get("/api/v1/customers", headers=headers)
    assert list_after_archive.status_code == 200
    assert list_after_archive.json() == []


def test_customer_contact_create_list(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    customer = create_customer(client, headers)

    create_response = client.post(
        f"/api/v1/customers/{customer['id']}/contacts",
        json={
            "full_name": "Elena Petrova",
            "phone": "+38970222333",
            "email": "elena@example.test",
            "role": "Owner",
            "note": "Primary customer contact",
            "is_primary": True,
        },
        headers=headers,
    )

    assert create_response.status_code == 201
    contact = create_response.json()
    assert contact["company_id"] == seeded_identity["demo_company_id"]
    assert contact["customer_id"] == customer["id"]
    assert contact["full_name"] == "Elena Petrova"
    assert contact["is_primary"] is True

    list_response = client.get(f"/api/v1/customers/{customer['id']}/contacts", headers=headers)
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [contact["id"]]


def test_property_create_list_detail_update_archive(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    customer = create_customer(client, headers)

    created = create_property(client, headers, str(customer["id"]))

    assert created["company_id"] == seeded_identity["demo_company_id"]
    assert created["customer_id"] == customer["id"]
    assert created["status"] == "active"
    assert created["archived_at"] is None

    list_response = client.get("/api/v1/properties", headers=headers)
    assert list_response.status_code == 200
    assert [property_item["id"] for property_item in list_response.json()] == [created["id"]]

    detail_response = client.get(f"/api/v1/properties/{created['id']}", headers=headers)
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == created["id"]

    update_response = client.patch(
        f"/api/v1/properties/{created['id']}",
        json={"name": "Updated Apartment Site", "city": "Bitola"},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated Apartment Site"
    assert update_response.json()["city"] == "Bitola"

    archive_response = client.post(f"/api/v1/properties/{created['id']}/archive", headers=headers)
    assert archive_response.status_code == 200
    assert archive_response.json()["status"] == "archived"
    assert archive_response.json()["archived_at"] is not None

    list_after_archive = client.get("/api/v1/properties", headers=headers)
    assert list_after_archive.status_code == 200
    assert list_after_archive.json() == []


def test_property_contact_create_list(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    customer = create_customer(client, headers)
    property_item = create_property(client, headers, str(customer["id"]))

    create_response = client.post(
        f"/api/v1/properties/{property_item['id']}/contacts",
        json={
            "full_name": "Bojan Manager",
            "phone": "+38970333444",
            "email": "bojan@example.test",
            "role": "Building manager",
            "note": "Has keys",
            "is_primary": False,
        },
        headers=headers,
    )

    assert create_response.status_code == 201
    contact = create_response.json()
    assert contact["company_id"] == seeded_identity["demo_company_id"]
    assert contact["property_id"] == property_item["id"]
    assert contact["full_name"] == "Bojan Manager"

    list_response = client.get(f"/api/v1/properties/{property_item['id']}/contacts", headers=headers)
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [contact["id"]]


def test_property_note_create_list(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    customer = create_customer(client, headers)
    property_item = create_property(client, headers, str(customer["id"]))

    create_response = client.post(
        f"/api/v1/properties/{property_item['id']}/notes",
        json={"content": "Entrance is from the north side."},
        headers=headers,
    )

    assert create_response.status_code == 201
    note = create_response.json()
    assert note["company_id"] == seeded_identity["demo_company_id"]
    assert note["property_id"] == property_item["id"]
    assert note["content"] == "Entrance is from the north side."

    list_response = client.get(f"/api/v1/properties/{property_item['id']}/notes", headers=headers)
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [note["id"]]


def test_tenant_isolation_for_customers(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    owner = owner_headers(client, seeded_identity)
    other = other_headers(client, seeded_identity)
    customer = create_customer(client, other, name="Other Company Customer")

    assert client.get(f"/api/v1/customers/{customer['id']}", headers=owner).status_code == 404
    assert (
        client.patch(
            f"/api/v1/customers/{customer['id']}",
            json={"name": "Cross tenant update"},
            headers=owner,
        ).status_code
        == 404
    )
    assert client.post(f"/api/v1/customers/{customer['id']}/archive", headers=owner).status_code == 404

    list_response = client.get("/api/v1/customers", headers=owner)
    assert list_response.status_code == 200
    assert list_response.json() == []


def test_tenant_isolation_for_properties(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    owner = owner_headers(client, seeded_identity)
    other = other_headers(client, seeded_identity)
    other_customer = create_customer(client, other, name="Other Company Customer")
    other_property = create_property(client, other, str(other_customer["id"]))

    assert client.get(f"/api/v1/properties/{other_property['id']}", headers=owner).status_code == 404
    assert (
        client.patch(
            f"/api/v1/properties/{other_property['id']}",
            json={"name": "Cross tenant property update"},
            headers=owner,
        ).status_code
        == 404
    )
    assert client.post(f"/api/v1/properties/{other_property['id']}/archive", headers=owner).status_code == 404

    list_response = client.get("/api/v1/properties", headers=owner)
    assert list_response.status_code == 200
    assert list_response.json() == []


def test_customer_property_endpoints_require_authentication(client: TestClient) -> None:
    endpoints: Iterable[tuple[str, str, Optional[dict[str, str]]]] = [
        ("post", "/api/v1/customers", {"name": "No Auth"}),
        ("get", "/api/v1/customers", None),
        ("get", "/api/v1/customers/missing", None),
        ("patch", "/api/v1/customers/missing", {"name": "No Auth"}),
        ("post", "/api/v1/customers/missing/archive", None),
        ("post", "/api/v1/customers/missing/contacts", {"full_name": "No Auth"}),
        ("get", "/api/v1/customers/missing/contacts", None),
        ("post", "/api/v1/properties", {"customer_id": "missing", "name": "No Auth"}),
        ("get", "/api/v1/properties", None),
        ("get", "/api/v1/properties/missing", None),
        ("patch", "/api/v1/properties/missing", {"name": "No Auth"}),
        ("post", "/api/v1/properties/missing/archive", None),
        ("post", "/api/v1/properties/missing/contacts", {"full_name": "No Auth"}),
        ("get", "/api/v1/properties/missing/contacts", None),
        ("post", "/api/v1/properties/missing/notes", {"content": "No Auth"}),
        ("get", "/api/v1/properties/missing/notes", None),
    ]

    for method, endpoint, payload in endpoints:
        request = getattr(client, method)
        response = request(endpoint, json=payload) if payload is not None else request(endpoint)
        assert response.status_code == 401, endpoint
