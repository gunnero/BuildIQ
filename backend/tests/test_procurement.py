from collections.abc import Iterable
from typing import Optional

from fastapi.testclient import TestClient

from tests.test_customers_properties import other_headers, owner_headers
from tests.test_materials import create_material
from tests.test_projects_tasks import create_project_fixture


def create_supplier(
    client: TestClient,
    headers: dict[str, str],
    *,
    name: str = "Build Supply",
) -> dict[str, object]:
    response = client.post(
        "/api/v1/suppliers",
        json={
            "name": name,
            "supplier_type": "supplier",
            "tax_number": "MK123456",
            "phone": "+38970123456",
            "email": "supplier@example.test",
            "address": "Industrial 1",
            "note": "Primary supplier",
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def create_supplier_contact(
    client: TestClient,
    headers: dict[str, str],
    supplier_id: str,
) -> dict[str, object]:
    response = client.post(
        f"/api/v1/suppliers/{supplier_id}/contacts",
        json={
            "full_name": "Elena Supplier",
            "phone": "+38970222333",
            "email": "elena@supplier.example.test",
            "role": "Sales",
            "note": "Handles contractor orders",
            "is_primary": True,
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def create_supplier_agreement(
    client: TestClient,
    headers: dict[str, str],
    supplier_id: str,
    *,
    agreement_number: str = "AGR-001",
    status: str = "active",
) -> dict[str, object]:
    response = client.post(
        f"/api/v1/suppliers/{supplier_id}/agreements",
        json={
            "agreement_number": agreement_number,
            "status": status,
            "starts_on": "2026-01-01",
            "ends_on": "2026-12-31",
            "terms_snapshot": {"discount_percent": 10, "payment_terms": "15 days"},
            "notes": "Negotiated contractor terms",
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def create_price_book(
    client: TestClient,
    headers: dict[str, str],
    *,
    supplier_id: Optional[str] = None,
    supplier_agreement_id: Optional[str] = None,
    name: str = "Retail prices",
    price_type: str = "retail",
    valid_from: str = "2026-01-01",
    valid_until: Optional[str] = "2026-12-31",
) -> dict[str, object]:
    response = client.post(
        "/api/v1/price-books",
        json={
            "supplier_id": supplier_id,
            "supplier_agreement_id": supplier_agreement_id,
            "name": name,
            "price_type": price_type,
            "status": "active",
            "currency": "MKD",
            "valid_from": valid_from,
            "valid_until": valid_until,
            "notes": "Price book notes",
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def create_price_book_item(
    client: TestClient,
    headers: dict[str, str],
    price_book_id: str,
    material_id: str,
    *,
    supplier_id: Optional[str] = None,
    unit_price: float = 100.0,
    valid_from: str = "2026-01-01",
    valid_until: Optional[str] = "2026-12-31",
) -> dict[str, object]:
    response = client.post(
        f"/api/v1/price-books/{price_book_id}/items",
        json={
            "material_id": material_id,
            "supplier_id": supplier_id,
            "supplier_sku": "SUP-PAINT-001",
            "unit_price": unit_price,
            "currency": "MKD",
            "valid_from": valid_from,
            "valid_until": valid_until,
            "notes": "Item price notes",
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def create_material_price_override(
    client: TestClient,
    headers: dict[str, str],
    project_id: str,
    material_id: str,
    *,
    supplier_id: Optional[str] = None,
    unit_price: float = 70.0,
    valid_from: str = "2026-01-01",
    valid_until: Optional[str] = "2026-12-31",
) -> dict[str, object]:
    response = client.post(
        f"/api/v1/projects/{project_id}/material-price-overrides",
        json={
            "material_id": material_id,
            "supplier_id": supplier_id,
            "unit_price": unit_price,
            "currency": "MKD",
            "valid_from": valid_from,
            "valid_until": valid_until,
            "reason": "Approved project discount",
            "notes": "Override notes",
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def test_supplier_create_list_detail_update_archive(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)

    created = create_supplier(client, headers)

    assert created["company_id"] == seeded_identity["demo_company_id"]
    assert created["name"] == "Build Supply"
    assert created["supplier_type"] == "supplier"
    assert created["status"] == "active"
    assert created["archived_at"] is None

    list_response = client.get("/api/v1/suppliers", headers=headers)
    assert list_response.status_code == 200
    assert [supplier["id"] for supplier in list_response.json()] == [created["id"]]

    detail_response = client.get(f"/api/v1/suppliers/{created['id']}", headers=headers)
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == created["id"]

    update_response = client.patch(
        f"/api/v1/suppliers/{created['id']}",
        json={"name": "Build Supply Pro", "note": "Updated note"},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Build Supply Pro"
    assert update_response.json()["note"] == "Updated note"

    archive_response = client.post(f"/api/v1/suppliers/{created['id']}/archive", headers=headers)
    assert archive_response.status_code == 200
    assert archive_response.json()["status"] == "archived"
    assert archive_response.json()["archived_at"] is not None

    list_after_archive = client.get("/api/v1/suppliers", headers=headers)
    assert list_after_archive.status_code == 200
    assert list_after_archive.json() == []


def test_supplier_contact_create_list_update_archive(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    supplier = create_supplier(client, headers)

    contact = create_supplier_contact(client, headers, str(supplier["id"]))

    assert contact["company_id"] == seeded_identity["demo_company_id"]
    assert contact["supplier_id"] == supplier["id"]
    assert contact["full_name"] == "Elena Supplier"
    assert contact["is_primary"] is True

    list_response = client.get(f"/api/v1/suppliers/{supplier['id']}/contacts", headers=headers)
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [contact["id"]]

    update_response = client.patch(
        f"/api/v1/supplier-contacts/{contact['id']}",
        json={"full_name": "Elena Updated", "is_primary": False},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["full_name"] == "Elena Updated"
    assert update_response.json()["is_primary"] is False

    archive_response = client.post(
        f"/api/v1/supplier-contacts/{contact['id']}/archive",
        headers=headers,
    )
    assert archive_response.status_code == 200
    assert archive_response.json()["archived_at"] is not None

    list_after_archive = client.get(f"/api/v1/suppliers/{supplier['id']}/contacts", headers=headers)
    assert list_after_archive.status_code == 200
    assert list_after_archive.json() == []


def test_supplier_agreement_create_list_detail_update_archive(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    supplier = create_supplier(client, headers)

    agreement = create_supplier_agreement(client, headers, str(supplier["id"]))

    assert agreement["company_id"] == seeded_identity["demo_company_id"]
    assert agreement["supplier_id"] == supplier["id"]
    assert agreement["agreement_number"] == "AGR-001"
    assert agreement["status"] == "active"
    assert agreement["terms_snapshot"]["discount_percent"] == 10

    list_response = client.get(f"/api/v1/suppliers/{supplier['id']}/agreements", headers=headers)
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [agreement["id"]]

    detail_response = client.get(f"/api/v1/supplier-agreements/{agreement['id']}", headers=headers)
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == agreement["id"]

    update_response = client.patch(
        f"/api/v1/supplier-agreements/{agreement['id']}",
        json={"status": "paused", "notes": "Paused by supplier"},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "paused"
    assert update_response.json()["notes"] == "Paused by supplier"

    archive_response = client.post(
        f"/api/v1/supplier-agreements/{agreement['id']}/archive",
        headers=headers,
    )
    assert archive_response.status_code == 200
    assert archive_response.json()["status"] == "archived"
    assert archive_response.json()["archived_at"] is not None


def test_price_book_create_list_detail_update_archive(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    supplier = create_supplier(client, headers)
    agreement = create_supplier_agreement(client, headers, str(supplier["id"]))

    price_book = create_price_book(
        client,
        headers,
        supplier_id=str(supplier["id"]),
        supplier_agreement_id=str(agreement["id"]),
        price_type="negotiated",
        name="Negotiated prices",
    )

    assert price_book["company_id"] == seeded_identity["demo_company_id"]
    assert price_book["supplier_id"] == supplier["id"]
    assert price_book["supplier_agreement_id"] == agreement["id"]
    assert price_book["price_type"] == "negotiated"
    assert price_book["currency"] == "MKD"

    list_response = client.get("/api/v1/price-books", headers=headers)
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [price_book["id"]]

    detail_response = client.get(f"/api/v1/price-books/{price_book['id']}", headers=headers)
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == price_book["id"]

    update_response = client.patch(
        f"/api/v1/price-books/{price_book['id']}",
        json={"name": "Updated negotiated prices", "notes": "Updated notes"},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated negotiated prices"

    archive_response = client.post(f"/api/v1/price-books/{price_book['id']}/archive", headers=headers)
    assert archive_response.status_code == 200
    assert archive_response.json()["status"] == "archived"
    assert archive_response.json()["archived_at"] is not None


def test_price_book_item_create_list_update_archive(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    supplier = create_supplier(client, headers)
    material = create_material(client, headers)
    price_book = create_price_book(client, headers, supplier_id=str(supplier["id"]))

    item = create_price_book_item(
        client,
        headers,
        str(price_book["id"]),
        str(material["id"]),
        supplier_id=str(supplier["id"]),
    )

    assert item["company_id"] == seeded_identity["demo_company_id"]
    assert item["price_book_id"] == price_book["id"]
    assert item["material_id"] == material["id"]
    assert item["supplier_id"] == supplier["id"]
    assert item["unit_price"] == 100.0
    assert item["currency"] == "MKD"

    list_response = client.get(f"/api/v1/price-books/{price_book['id']}/items", headers=headers)
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [item["id"]]

    update_response = client.patch(
        f"/api/v1/price-book-items/{item['id']}",
        json={"unit_price": 95.0, "notes": "Corrected price"},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["unit_price"] == 95.0
    assert update_response.json()["notes"] == "Corrected price"

    archive_response = client.post(
        f"/api/v1/price-book-items/{item['id']}/archive",
        headers=headers,
    )
    assert archive_response.status_code == 200
    assert archive_response.json()["archived_at"] is not None

    list_after_archive = client.get(f"/api/v1/price-books/{price_book['id']}/items", headers=headers)
    assert list_after_archive.status_code == 200
    assert list_after_archive.json() == []


def test_project_override_create_list_update_archive(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    supplier = create_supplier(client, headers)
    material = create_material(client, headers)
    _, _, project = create_project_fixture(client, headers)

    override = create_material_price_override(
        client,
        headers,
        str(project["id"]),
        str(material["id"]),
        supplier_id=str(supplier["id"]),
    )

    assert override["company_id"] == seeded_identity["demo_company_id"]
    assert override["project_id"] == project["id"]
    assert override["material_id"] == material["id"]
    assert override["supplier_id"] == supplier["id"]
    assert override["unit_price"] == 70.0
    assert override["created_by_user_id"] == seeded_identity["owner_user_id"]

    list_response = client.get(
        f"/api/v1/projects/{project['id']}/material-price-overrides",
        headers=headers,
    )
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [override["id"]]

    update_response = client.patch(
        f"/api/v1/material-price-overrides/{override['id']}",
        json={"unit_price": 68.0, "reason": "Updated project approval"},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["unit_price"] == 68.0
    assert update_response.json()["reason"] == "Updated project approval"

    archive_response = client.post(
        f"/api/v1/material-price-overrides/{override['id']}/archive",
        headers=headers,
    )
    assert archive_response.status_code == 200
    assert archive_response.json()["archived_at"] is not None

    list_after_archive = client.get(
        f"/api/v1/projects/{project['id']}/material-price-overrides",
        headers=headers,
    )
    assert list_after_archive.status_code == 200
    assert list_after_archive.json() == []


def test_price_resolution_uses_project_override_first(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    supplier = create_supplier(client, headers)
    material = create_material(client, headers)
    _, _, project = create_project_fixture(client, headers)
    retail_book = create_price_book(client, headers, supplier_id=str(supplier["id"]), price_type="retail")
    create_price_book_item(
        client,
        headers,
        str(retail_book["id"]),
        str(material["id"]),
        supplier_id=str(supplier["id"]),
        unit_price=100.0,
    )
    negotiated_book = create_price_book(
        client,
        headers,
        supplier_id=str(supplier["id"]),
        price_type="negotiated",
        name="Negotiated prices",
    )
    create_price_book_item(
        client,
        headers,
        str(negotiated_book["id"]),
        str(material["id"]),
        supplier_id=str(supplier["id"]),
        unit_price=80.0,
    )
    override = create_material_price_override(
        client,
        headers,
        str(project["id"]),
        str(material["id"]),
        supplier_id=str(supplier["id"]),
        unit_price=70.0,
    )

    response = client.get(
        f"/api/v1/projects/{project['id']}/materials/{material['id']}/resolved-price",
        headers=headers,
    )

    assert response.status_code == 200
    resolved = response.json()
    assert resolved["material_id"] == material["id"]
    assert resolved["supplier_id"] == supplier["id"]
    assert resolved["resolved_price"] == 70.0
    assert resolved["currency"] == "MKD"
    assert resolved["source_type"] == "project_override"
    assert resolved["source_id"] == override["id"]
    assert resolved["notes"] == "Override notes"


def test_price_resolution_uses_negotiated_price_book_second(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    supplier = create_supplier(client, headers)
    material = create_material(client, headers)
    _, _, project = create_project_fixture(client, headers)
    retail_book = create_price_book(client, headers, supplier_id=str(supplier["id"]), price_type="retail")
    create_price_book_item(
        client,
        headers,
        str(retail_book["id"]),
        str(material["id"]),
        supplier_id=str(supplier["id"]),
        unit_price=100.0,
    )
    negotiated_book = create_price_book(
        client,
        headers,
        supplier_id=str(supplier["id"]),
        price_type="negotiated",
        name="Negotiated prices",
    )
    negotiated_item = create_price_book_item(
        client,
        headers,
        str(negotiated_book["id"]),
        str(material["id"]),
        supplier_id=str(supplier["id"]),
        unit_price=80.0,
    )

    response = client.get(
        f"/api/v1/projects/{project['id']}/materials/{material['id']}/resolved-price",
        headers=headers,
    )

    assert response.status_code == 200
    resolved = response.json()
    assert resolved["resolved_price"] == 80.0
    assert resolved["source_type"] == "negotiated_price_book"
    assert resolved["source_id"] == negotiated_item["id"]


def test_price_resolution_uses_retail_price_book_third(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    supplier = create_supplier(client, headers)
    material = create_material(client, headers)
    retail_book = create_price_book(client, headers, supplier_id=str(supplier["id"]), price_type="retail")
    retail_item = create_price_book_item(
        client,
        headers,
        str(retail_book["id"]),
        str(material["id"]),
        supplier_id=str(supplier["id"]),
        unit_price=100.0,
    )

    response = client.get(f"/api/v1/materials/{material['id']}/resolved-price", headers=headers)

    assert response.status_code == 200
    resolved = response.json()
    assert resolved["resolved_price"] == 100.0
    assert resolved["source_type"] == "retail_price_book"
    assert resolved["source_id"] == retail_item["id"]


def test_price_resolution_returns_none_when_no_price_exists(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    material = create_material(client, headers)

    response = client.get(f"/api/v1/materials/{material['id']}/resolved-price", headers=headers)

    assert response.status_code == 200
    assert response.json() == {
        "material_id": material["id"],
        "supplier_id": None,
        "resolved_price": None,
        "currency": None,
        "source_type": "none",
        "source_id": None,
        "valid_from": None,
        "valid_until": None,
        "notes": None,
    }


def test_price_resolution_respects_validity_dates(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    supplier = create_supplier(client, headers)
    material = create_material(client, headers)
    _, _, project = create_project_fixture(client, headers)
    expired_negotiated_book = create_price_book(
        client,
        headers,
        supplier_id=str(supplier["id"]),
        price_type="negotiated",
        name="Expired negotiated prices",
        valid_from="2026-01-01",
        valid_until="2026-01-31",
    )
    create_price_book_item(
        client,
        headers,
        str(expired_negotiated_book["id"]),
        str(material["id"]),
        supplier_id=str(supplier["id"]),
        unit_price=80.0,
        valid_from="2026-01-01",
        valid_until="2026-01-31",
    )
    create_material_price_override(
        client,
        headers,
        str(project["id"]),
        str(material["id"]),
        supplier_id=str(supplier["id"]),
        unit_price=70.0,
        valid_from="2026-01-01",
        valid_until="2026-01-31",
    )
    retail_book = create_price_book(
        client,
        headers,
        supplier_id=str(supplier["id"]),
        price_type="retail",
        valid_from="2026-01-01",
        valid_until="2027-01-01",
    )
    retail_item = create_price_book_item(
        client,
        headers,
        str(retail_book["id"]),
        str(material["id"]),
        supplier_id=str(supplier["id"]),
        unit_price=100.0,
        valid_from="2026-01-01",
        valid_until="2027-01-01",
    )

    response = client.get(
        f"/api/v1/projects/{project['id']}/materials/{material['id']}/resolved-price",
        headers=headers,
    )

    assert response.status_code == 200
    resolved = response.json()
    assert resolved["resolved_price"] == 100.0
    assert resolved["source_type"] == "retail_price_book"
    assert resolved["source_id"] == retail_item["id"]


def test_tenant_isolation_for_all_procurement_records(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    owner = owner_headers(client, seeded_identity)
    other = other_headers(client, seeded_identity)
    other_supplier = create_supplier(client, other, name="Other supplier")
    other_contact = create_supplier_contact(client, other, str(other_supplier["id"]))
    other_agreement = create_supplier_agreement(client, other, str(other_supplier["id"]))
    other_material = create_material(client, other, name="Other material")
    _, _, other_project = create_project_fixture(client, other)
    other_price_book = create_price_book(
        client,
        other,
        supplier_id=str(other_supplier["id"]),
        supplier_agreement_id=str(other_agreement["id"]),
        price_type="negotiated",
    )
    other_item = create_price_book_item(
        client,
        other,
        str(other_price_book["id"]),
        str(other_material["id"]),
        supplier_id=str(other_supplier["id"]),
    )
    other_override = create_material_price_override(
        client,
        other,
        str(other_project["id"]),
        str(other_material["id"]),
        supplier_id=str(other_supplier["id"]),
    )

    assert client.get(f"/api/v1/suppliers/{other_supplier['id']}", headers=owner).status_code == 404
    assert (
        client.patch(
            f"/api/v1/suppliers/{other_supplier['id']}",
            json={"name": "Cross tenant"},
            headers=owner,
        ).status_code
        == 404
    )
    assert client.post(f"/api/v1/suppliers/{other_supplier['id']}/archive", headers=owner).status_code == 404
    assert client.get(f"/api/v1/suppliers/{other_supplier['id']}/contacts", headers=owner).status_code == 404
    assert (
        client.patch(
            f"/api/v1/supplier-contacts/{other_contact['id']}",
            json={"full_name": "Cross tenant"},
            headers=owner,
        ).status_code
        == 404
    )
    assert client.post(f"/api/v1/supplier-contacts/{other_contact['id']}/archive", headers=owner).status_code == 404
    assert client.get(f"/api/v1/supplier-agreements/{other_agreement['id']}", headers=owner).status_code == 404
    assert (
        client.patch(
            f"/api/v1/supplier-agreements/{other_agreement['id']}",
            json={"status": "paused"},
            headers=owner,
        ).status_code
        == 404
    )
    assert (
        client.post(
            f"/api/v1/supplier-agreements/{other_agreement['id']}/archive",
            headers=owner,
        ).status_code
        == 404
    )
    assert client.get(f"/api/v1/price-books/{other_price_book['id']}", headers=owner).status_code == 404
    assert (
        client.patch(
            f"/api/v1/price-books/{other_price_book['id']}",
            json={"name": "Cross tenant"},
            headers=owner,
        ).status_code
        == 404
    )
    assert client.post(f"/api/v1/price-books/{other_price_book['id']}/archive", headers=owner).status_code == 404
    assert client.get(f"/api/v1/price-books/{other_price_book['id']}/items", headers=owner).status_code == 404
    assert (
        client.patch(
            f"/api/v1/price-book-items/{other_item['id']}",
            json={"unit_price": 1.0},
            headers=owner,
        ).status_code
        == 404
    )
    assert client.post(f"/api/v1/price-book-items/{other_item['id']}/archive", headers=owner).status_code == 404
    assert (
        client.get(
            f"/api/v1/projects/{other_project['id']}/material-price-overrides",
            headers=owner,
        ).status_code
        == 404
    )
    assert (
        client.patch(
            f"/api/v1/material-price-overrides/{other_override['id']}",
            json={"unit_price": 1.0},
            headers=owner,
        ).status_code
        == 404
    )
    assert (
        client.post(
            f"/api/v1/material-price-overrides/{other_override['id']}/archive",
            headers=owner,
        ).status_code
        == 404
    )

    assert client.get("/api/v1/suppliers", headers=owner).json() == []
    assert client.get("/api/v1/price-books", headers=owner).json() == []


def test_invalid_cross_company_supplier_material_project_links_are_rejected(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    owner = owner_headers(client, seeded_identity)
    other = other_headers(client, seeded_identity)
    owner_supplier = create_supplier(client, owner)
    owner_material = create_material(client, owner)
    _, _, owner_project = create_project_fixture(client, owner)
    owner_price_book = create_price_book(client, owner, supplier_id=str(owner_supplier["id"]))
    other_supplier = create_supplier(client, other, name="Other supplier")
    other_material = create_material(client, other, name="Other material")
    _, _, other_project = create_project_fixture(client, other)
    other_agreement = create_supplier_agreement(client, other, str(other_supplier["id"]))

    assert (
        client.post(
            f"/api/v1/suppliers/{other_supplier['id']}/contacts",
            json={"full_name": "Cross tenant"},
            headers=owner,
        ).status_code
        == 404
    )
    assert (
        client.post(
            f"/api/v1/suppliers/{other_supplier['id']}/agreements",
            json={"agreement_number": "BAD-001"},
            headers=owner,
        ).status_code
        == 404
    )
    assert (
        client.post(
            "/api/v1/price-books",
            json={"supplier_id": other_supplier["id"], "name": "Bad price book", "price_type": "retail"},
            headers=owner,
        ).status_code
        == 404
    )
    assert (
        client.post(
            "/api/v1/price-books",
            json={
                "supplier_id": owner_supplier["id"],
                "supplier_agreement_id": other_agreement["id"],
                "name": "Bad agreement",
                "price_type": "negotiated",
            },
            headers=owner,
        ).status_code
        == 404
    )
    assert (
        client.post(
            f"/api/v1/price-books/{owner_price_book['id']}/items",
            json={
                "material_id": other_material["id"],
                "unit_price": 1.0,
                "currency": "MKD",
                "valid_from": "2026-01-01",
            },
            headers=owner,
        ).status_code
        == 404
    )
    assert (
        client.post(
            f"/api/v1/price-books/{owner_price_book['id']}/items",
            json={
                "material_id": owner_material["id"],
                "supplier_id": other_supplier["id"],
                "unit_price": 1.0,
                "currency": "MKD",
                "valid_from": "2026-01-01",
            },
            headers=owner,
        ).status_code
        == 404
    )
    assert (
        client.post(
            f"/api/v1/projects/{other_project['id']}/material-price-overrides",
            json={"material_id": owner_material["id"], "unit_price": 1.0, "valid_from": "2026-01-01"},
            headers=owner,
        ).status_code
        == 404
    )
    assert (
        client.post(
            f"/api/v1/projects/{owner_project['id']}/material-price-overrides",
            json={"material_id": other_material["id"], "unit_price": 1.0, "valid_from": "2026-01-01"},
            headers=owner,
        ).status_code
        == 404
    )
    assert (
        client.post(
            f"/api/v1/projects/{owner_project['id']}/material-price-overrides",
            json={
                "material_id": owner_material["id"],
                "supplier_id": other_supplier["id"],
                "unit_price": 1.0,
                "valid_from": "2026-01-01",
            },
            headers=owner,
        ).status_code
        == 404
    )


def test_procurement_endpoints_require_authentication(client: TestClient) -> None:
    endpoints: Iterable[tuple[str, str, Optional[dict[str, object]]]] = [
        ("post", "/api/v1/suppliers", {"name": "No Auth"}),
        ("get", "/api/v1/suppliers", None),
        ("get", "/api/v1/suppliers/missing", None),
        ("patch", "/api/v1/suppliers/missing", {"name": "No Auth"}),
        ("post", "/api/v1/suppliers/missing/archive", None),
        ("post", "/api/v1/suppliers/missing/contacts", {"full_name": "No Auth"}),
        ("get", "/api/v1/suppliers/missing/contacts", None),
        ("patch", "/api/v1/supplier-contacts/missing", {"full_name": "No Auth"}),
        ("post", "/api/v1/supplier-contacts/missing/archive", None),
        ("post", "/api/v1/suppliers/missing/agreements", {"agreement_number": "No Auth"}),
        ("get", "/api/v1/suppliers/missing/agreements", None),
        ("get", "/api/v1/supplier-agreements/missing", None),
        ("patch", "/api/v1/supplier-agreements/missing", {"status": "active"}),
        ("post", "/api/v1/supplier-agreements/missing/archive", None),
        ("post", "/api/v1/price-books", {"name": "No Auth", "price_type": "retail"}),
        ("get", "/api/v1/price-books", None),
        ("get", "/api/v1/price-books/missing", None),
        ("patch", "/api/v1/price-books/missing", {"name": "No Auth"}),
        ("post", "/api/v1/price-books/missing/archive", None),
        (
            "post",
            "/api/v1/price-books/missing/items",
            {"material_id": "missing", "unit_price": 1, "valid_from": "2026-01-01"},
        ),
        ("get", "/api/v1/price-books/missing/items", None),
        ("patch", "/api/v1/price-book-items/missing", {"unit_price": 1}),
        ("post", "/api/v1/price-book-items/missing/archive", None),
        (
            "post",
            "/api/v1/projects/missing/material-price-overrides",
            {"material_id": "missing", "unit_price": 1, "valid_from": "2026-01-01"},
        ),
        ("get", "/api/v1/projects/missing/material-price-overrides", None),
        ("patch", "/api/v1/material-price-overrides/missing", {"unit_price": 1}),
        ("post", "/api/v1/material-price-overrides/missing/archive", None),
        ("get", "/api/v1/materials/missing/resolved-price", None),
        ("get", "/api/v1/projects/missing/materials/missing/resolved-price", None),
    ]

    for method, endpoint, payload in endpoints:
        request = getattr(client, method)
        response = request(endpoint, json=payload) if payload is not None else request(endpoint)
        assert response.status_code == 401, endpoint
