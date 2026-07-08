from collections.abc import Iterable
from typing import Optional

from fastapi.testclient import TestClient

from tests.test_customers_properties import other_headers, owner_headers


DEFAULT_UNIT_KEYS = {
    "piece",
    "m",
    "m2",
    "m3",
    "kg",
    "liter",
    "bag",
    "bucket",
    "roll",
    "hour",
}


def create_material_category(
    client: TestClient,
    headers: dict[str, str],
    *,
    name: str = "Paints",
) -> dict[str, object]:
    response = client.post(
        "/api/v1/material-categories",
        json={"name": name, "description": "Material category"},
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def create_material_manufacturer(
    client: TestClient,
    headers: dict[str, str],
    *,
    name: str = "BuildCo",
) -> dict[str, object]:
    response = client.post(
        "/api/v1/material-manufacturers",
        json={"name": name, "website": "https://example.test", "note": "Preferred brand"},
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def material_unit_by_key(
    client: TestClient,
    headers: dict[str, str],
    key: str = "liter",
) -> dict[str, object]:
    response = client.get("/api/v1/material-units", headers=headers)
    assert response.status_code == 200
    unit = next(item for item in response.json() if item["key"] == key)
    return unit


def create_custom_material_unit(
    client: TestClient,
    headers: dict[str, str],
    *,
    key: str = "box",
    name: str = "Box",
) -> dict[str, object]:
    response = client.post(
        "/api/v1/material-units",
        json={"key": key, "name": name, "description": "Company-specific unit"},
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def create_material(
    client: TestClient,
    headers: dict[str, str],
    *,
    name: str = "Interior paint",
    category_id: Optional[str] = None,
    manufacturer_id: Optional[str] = None,
    unit_id: Optional[str] = None,
) -> dict[str, object]:
    if unit_id is None:
        unit_id = str(material_unit_by_key(client, headers, "liter")["id"])
    response = client.post(
        "/api/v1/materials",
        json={
            "name": name,
            "sku": "PAINT-001",
            "description": "Washable interior paint",
            "category_id": category_id,
            "manufacturer_id": manufacturer_id,
            "unit_id": unit_id,
            "coverage_value": 10.0,
            "coverage_unit": "m2/liter",
            "package_quantity": 15.0,
            "waste_percentage_default": 5.0,
            "is_active": True,
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def create_consumption_rule(
    client: TestClient,
    headers: dict[str, str],
    material_id: str,
    *,
    engine_type: str = "painting",
) -> dict[str, object]:
    response = client.post(
        "/api/v1/material-consumption-rules",
        json={
            "material_id": material_id,
            "engine_type": engine_type,
            "name": "Paint coverage",
            "input_unit": "m2",
            "consumption_rate": 0.1,
            "waste_percentage": 5.0,
            "description": "Liters per square meter",
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def test_material_category_create_list_update_archive(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)

    created = create_material_category(client, headers)

    assert created["company_id"] == seeded_identity["demo_company_id"]
    assert created["name"] == "Paints"
    assert created["archived_at"] is None

    list_response = client.get("/api/v1/material-categories", headers=headers)
    assert list_response.status_code == 200
    assert [category["id"] for category in list_response.json()] == [created["id"]]

    update_response = client.patch(
        f"/api/v1/material-categories/{created['id']}",
        json={"name": "Wall paints", "description": "Updated category"},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Wall paints"
    assert update_response.json()["description"] == "Updated category"

    archive_response = client.post(
        f"/api/v1/material-categories/{created['id']}/archive",
        headers=headers,
    )
    assert archive_response.status_code == 200
    assert archive_response.json()["archived_at"] is not None

    list_after_archive = client.get("/api/v1/material-categories", headers=headers)
    assert list_after_archive.status_code == 200
    assert list_after_archive.json() == []


def test_material_manufacturer_create_list_update_archive(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)

    created = create_material_manufacturer(client, headers)

    assert created["company_id"] == seeded_identity["demo_company_id"]
    assert created["name"] == "BuildCo"
    assert created["website"] == "https://example.test"

    list_response = client.get("/api/v1/material-manufacturers", headers=headers)
    assert list_response.status_code == 200
    assert [manufacturer["id"] for manufacturer in list_response.json()] == [created["id"]]

    update_response = client.patch(
        f"/api/v1/material-manufacturers/{created['id']}",
        json={"name": "BuildCo Pro", "note": "Updated note"},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "BuildCo Pro"
    assert update_response.json()["note"] == "Updated note"

    archive_response = client.post(
        f"/api/v1/material-manufacturers/{created['id']}/archive",
        headers=headers,
    )
    assert archive_response.status_code == 200
    assert archive_response.json()["archived_at"] is not None

    list_after_archive = client.get("/api/v1/material-manufacturers", headers=headers)
    assert list_after_archive.status_code == 200
    assert list_after_archive.json() == []


def test_default_units_are_available(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)

    response = client.get("/api/v1/material-units", headers=headers)

    assert response.status_code == 200
    units = response.json()
    default_units = [unit for unit in units if unit["is_default"] is True]
    assert {unit["key"] for unit in default_units} == DEFAULT_UNIT_KEYS
    assert all(unit["company_id"] is None for unit in default_units)


def test_custom_company_unit_can_be_created(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)

    created = create_custom_material_unit(client, headers)

    assert created["company_id"] == seeded_identity["demo_company_id"]
    assert created["key"] == "box"
    assert created["is_default"] is False

    list_response = client.get("/api/v1/material-units", headers=headers)
    assert list_response.status_code == 200
    assert created["id"] in {unit["id"] for unit in list_response.json()}


def test_material_create_list_detail_update_archive(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    category = create_material_category(client, headers)
    manufacturer = create_material_manufacturer(client, headers)
    unit = material_unit_by_key(client, headers, "liter")

    created = create_material(
        client,
        headers,
        category_id=str(category["id"]),
        manufacturer_id=str(manufacturer["id"]),
        unit_id=str(unit["id"]),
    )

    assert created["company_id"] == seeded_identity["demo_company_id"]
    assert created["name"] == "Interior paint"
    assert created["sku"] == "PAINT-001"
    assert created["category_id"] == category["id"]
    assert created["manufacturer_id"] == manufacturer["id"]
    assert created["unit_id"] == unit["id"]
    assert created["coverage_value"] == 10.0
    assert created["coverage_unit"] == "m2/liter"
    assert created["package_quantity"] == 15.0
    assert created["waste_percentage_default"] == 5.0
    assert created["is_active"] is True
    assert created["archived_at"] is None

    list_response = client.get("/api/v1/materials", headers=headers)
    assert list_response.status_code == 200
    assert [material["id"] for material in list_response.json()] == [created["id"]]

    detail_response = client.get(f"/api/v1/materials/{created['id']}", headers=headers)
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == created["id"]

    update_response = client.patch(
        f"/api/v1/materials/{created['id']}",
        json={"name": "Premium interior paint", "coverage_value": 12.5},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Premium interior paint"
    assert update_response.json()["coverage_value"] == 12.5

    archive_response = client.post(f"/api/v1/materials/{created['id']}/archive", headers=headers)
    assert archive_response.status_code == 200
    assert archive_response.json()["is_active"] is False
    assert archive_response.json()["archived_at"] is not None

    list_after_archive = client.get("/api/v1/materials", headers=headers)
    assert list_after_archive.status_code == 200
    assert list_after_archive.json() == []


def test_material_validates_links_belong_to_same_company_or_allowed_defaults(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    owner = owner_headers(client, seeded_identity)
    other = other_headers(client, seeded_identity)
    owner_category = create_material_category(client, owner, name="Owner category")
    owner_unit = create_custom_material_unit(client, owner, key="pallet", name="Pallet")
    other_category = create_material_category(client, other, name="Other category")
    other_manufacturer = create_material_manufacturer(client, other, name="Other manufacturer")
    other_unit = create_custom_material_unit(client, other, key="crate", name="Crate")

    valid_with_default = client.post(
        "/api/v1/materials",
        json={
            "name": "Default unit material",
            "category_id": owner_category["id"],
            "unit_id": material_unit_by_key(client, owner, "piece")["id"],
        },
        headers=owner,
    )
    assert valid_with_default.status_code == 201

    valid_with_company_unit = client.post(
        "/api/v1/materials",
        json={"name": "Custom unit material", "unit_id": owner_unit["id"]},
        headers=owner,
    )
    assert valid_with_company_unit.status_code == 201

    cross_category = client.post(
        "/api/v1/materials",
        json={"name": "Cross category", "category_id": other_category["id"], "unit_id": owner_unit["id"]},
        headers=owner,
    )
    assert cross_category.status_code == 404

    cross_manufacturer = client.post(
        "/api/v1/materials",
        json={
            "name": "Cross manufacturer",
            "manufacturer_id": other_manufacturer["id"],
            "unit_id": owner_unit["id"],
        },
        headers=owner,
    )
    assert cross_manufacturer.status_code == 404

    cross_unit = client.post(
        "/api/v1/materials",
        json={"name": "Cross unit", "unit_id": other_unit["id"]},
        headers=owner,
    )
    assert cross_unit.status_code == 404


def test_consumption_rule_create_list_update_archive(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    material = create_material(client, headers)

    created = create_consumption_rule(client, headers, str(material["id"]))

    assert created["company_id"] == seeded_identity["demo_company_id"]
    assert created["material_id"] == material["id"]
    assert created["engine_type"] == "painting"
    assert created["consumption_rate"] == 0.1
    assert created["waste_percentage"] == 5.0

    list_response = client.get("/api/v1/material-consumption-rules", headers=headers)
    assert list_response.status_code == 200
    assert [rule["id"] for rule in list_response.json()] == [created["id"]]

    material_rules_response = client.get(
        f"/api/v1/materials/{material['id']}/consumption-rules",
        headers=headers,
    )
    assert material_rules_response.status_code == 200
    assert [rule["id"] for rule in material_rules_response.json()] == [created["id"]]

    update_response = client.patch(
        f"/api/v1/material-consumption-rules/{created['id']}",
        json={"name": "Updated coverage", "consumption_rate": 0.12},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated coverage"
    assert update_response.json()["consumption_rate"] == 0.12

    archive_response = client.post(
        f"/api/v1/material-consumption-rules/{created['id']}/archive",
        headers=headers,
    )
    assert archive_response.status_code == 200
    assert archive_response.json()["archived_at"] is not None

    list_after_archive = client.get("/api/v1/material-consumption-rules", headers=headers)
    assert list_after_archive.status_code == 200
    assert list_after_archive.json() == []


def test_consumption_rule_validates_material_belongs_to_same_company(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    owner = owner_headers(client, seeded_identity)
    other = other_headers(client, seeded_identity)
    other_material = create_material(client, other, name="Other material")

    response = client.post(
        "/api/v1/material-consumption-rules",
        json={
            "material_id": other_material["id"],
            "engine_type": "painting",
            "name": "Cross tenant rule",
        },
        headers=owner,
    )

    assert response.status_code == 404


def test_tenant_isolation_for_all_material_entities(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    owner = owner_headers(client, seeded_identity)
    other = other_headers(client, seeded_identity)
    other_category = create_material_category(client, other, name="Other category")
    other_manufacturer = create_material_manufacturer(client, other, name="Other manufacturer")
    other_unit = create_custom_material_unit(client, other, key="crate", name="Crate")
    other_material = create_material(
        client,
        other,
        name="Other material",
        category_id=str(other_category["id"]),
        manufacturer_id=str(other_manufacturer["id"]),
        unit_id=str(other_unit["id"]),
    )
    other_rule = create_consumption_rule(client, other, str(other_material["id"]), engine_type="tiles")

    assert (
        client.patch(
            f"/api/v1/material-categories/{other_category['id']}",
            json={"name": "Cross tenant"},
            headers=owner,
        ).status_code
        == 404
    )
    assert (
        client.post(
            f"/api/v1/material-categories/{other_category['id']}/archive",
            headers=owner,
        ).status_code
        == 404
    )
    assert (
        client.patch(
            f"/api/v1/material-manufacturers/{other_manufacturer['id']}",
            json={"name": "Cross tenant"},
            headers=owner,
        ).status_code
        == 404
    )
    assert (
        client.post(
            f"/api/v1/material-manufacturers/{other_manufacturer['id']}/archive",
            headers=owner,
        ).status_code
        == 404
    )
    assert client.get(f"/api/v1/materials/{other_material['id']}", headers=owner).status_code == 404
    assert (
        client.patch(
            f"/api/v1/materials/{other_material['id']}",
            json={"name": "Cross tenant material"},
            headers=owner,
        ).status_code
        == 404
    )
    assert client.post(f"/api/v1/materials/{other_material['id']}/archive", headers=owner).status_code == 404
    assert (
        client.get(
            f"/api/v1/materials/{other_material['id']}/consumption-rules",
            headers=owner,
        ).status_code
        == 404
    )
    assert (
        client.patch(
            f"/api/v1/material-consumption-rules/{other_rule['id']}",
            json={"name": "Cross tenant rule"},
            headers=owner,
        ).status_code
        == 404
    )
    assert (
        client.post(
            f"/api/v1/material-consumption-rules/{other_rule['id']}/archive",
            headers=owner,
        ).status_code
        == 404
    )

    owner_units = client.get("/api/v1/material-units", headers=owner)
    assert owner_units.status_code == 200
    assert other_unit["id"] not in {unit["id"] for unit in owner_units.json()}

    assert client.get("/api/v1/material-categories", headers=owner).json() == []
    assert client.get("/api/v1/material-manufacturers", headers=owner).json() == []
    assert client.get("/api/v1/materials", headers=owner).json() == []
    assert client.get("/api/v1/material-consumption-rules", headers=owner).json() == []


def test_material_endpoints_require_authentication(client: TestClient) -> None:
    endpoints: Iterable[tuple[str, str, Optional[dict[str, object]]]] = [
        ("post", "/api/v1/material-categories", {"name": "No Auth"}),
        ("get", "/api/v1/material-categories", None),
        ("patch", "/api/v1/material-categories/missing", {"name": "No Auth"}),
        ("post", "/api/v1/material-categories/missing/archive", None),
        ("post", "/api/v1/material-manufacturers", {"name": "No Auth"}),
        ("get", "/api/v1/material-manufacturers", None),
        ("patch", "/api/v1/material-manufacturers/missing", {"name": "No Auth"}),
        ("post", "/api/v1/material-manufacturers/missing/archive", None),
        ("get", "/api/v1/material-units", None),
        ("post", "/api/v1/material-units", {"key": "box", "name": "Box"}),
        ("post", "/api/v1/materials", {"name": "No Auth", "unit_id": "missing"}),
        ("get", "/api/v1/materials", None),
        ("get", "/api/v1/materials/missing", None),
        ("patch", "/api/v1/materials/missing", {"name": "No Auth"}),
        ("post", "/api/v1/materials/missing/archive", None),
        (
            "post",
            "/api/v1/material-consumption-rules",
            {"material_id": "missing", "engine_type": "painting", "name": "No Auth"},
        ),
        ("get", "/api/v1/material-consumption-rules", None),
        ("get", "/api/v1/materials/missing/consumption-rules", None),
        ("patch", "/api/v1/material-consumption-rules/missing", {"name": "No Auth"}),
        ("post", "/api/v1/material-consumption-rules/missing/archive", None),
    ]

    for method, endpoint, payload in endpoints:
        request = getattr(client, method)
        response = request(endpoint, json=payload) if payload is not None else request(endpoint)
        assert response.status_code == 401, endpoint
