from fastapi.testclient import TestClient

from tests.test_customers_properties import other_headers, owner_headers
from tests.test_painting_engine import assert_rounded, create_paint_material, run_painting
from tests.test_procurement import create_price_book, create_price_book_item, create_supplier
from tests.test_projects_tasks import create_project_fixture
from tests.test_rooms_measurements import create_room


def create_estimate(
    client: TestClient,
    headers: dict[str, str],
    project_id: str,
    *,
    title: str = "Apartment renovation offer",
) -> dict[str, object]:
    response = client.post(
        "/api/v1/estimates",
        json={
            "project_id": project_id,
            "title": title,
            "description": "Manual estimate",
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def first_revision(
    client: TestClient,
    headers: dict[str, str],
    estimate_id: str,
) -> dict[str, object]:
    response = client.get(f"/api/v1/estimates/{estimate_id}/revisions", headers=headers)
    assert response.status_code == 200
    revisions = response.json()
    assert len(revisions) == 1
    return revisions[0]


def create_estimate_item(
    client: TestClient,
    headers: dict[str, str],
    revision_id: str,
    *,
    item_type: str = "service",
    name: str = "Wall preparation",
    quantity: float = 1.0,
    unit_price: float = 1000.0,
    unit: str = "piece",
) -> dict[str, object]:
    response = client.post(
        f"/api/v1/estimate-revisions/{revision_id}/items",
        json={
            "item_type": item_type,
            "name": name,
            "description": "Estimate line",
            "quantity": quantity,
            "unit": unit,
            "unit_price": unit_price,
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def set_estimate_status(
    client: TestClient,
    headers: dict[str, str],
    estimate_id: str,
    status_value: str,
) -> dict[str, object]:
    response = client.post(
        f"/api/v1/estimates/{estimate_id}/status",
        json={"status": status_value, "note": "Customer update"},
        headers=headers,
    )
    assert response.status_code == 200
    return response.json()


def completed_painting_run(
    client: TestClient,
    headers: dict[str, str],
) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    _, _, project = create_project_fixture(client, headers)
    room = create_room(client, headers, str(project["id"]), length=5.0, width=4.0, height=3.0)
    paint = create_paint_material(client, headers, coverage_value=10.0, waste_percentage_default=10.0)
    supplier = create_supplier(client, headers)
    price_book = create_price_book(client, headers, supplier_id=str(supplier["id"]), price_type="retail")
    create_price_book_item(
        client,
        headers,
        str(price_book["id"]),
        str(paint["id"]),
        supplier_id=str(supplier["id"]),
        unit_price=200.0,
    )
    calculation = run_painting(
        client,
        headers,
        project_id=str(project["id"]),
        room_id=str(room["id"]),
        input_payload={
            "paint_material_id": paint["id"],
            "labor_rate_per_m2": 120.0,
        },
    )
    assert calculation["status"] == "completed"
    return project, paint, calculation


def test_estimate_create_list_detail_update_archive(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    customer, property_item, project = create_project_fixture(client, headers)

    estimate = create_estimate(client, headers, str(project["id"]))

    assert estimate["company_id"] == seeded_identity["demo_company_id"]
    assert estimate["customer_id"] == customer["id"]
    assert estimate["property_id"] == property_item["id"]
    assert estimate["project_id"] == project["id"]
    assert estimate["status"] == "draft"
    assert estimate["archived_at"] is None

    list_response = client.get("/api/v1/estimates", headers=headers)
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [estimate["id"]]

    detail_response = client.get(f"/api/v1/estimates/{estimate['id']}", headers=headers)
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == estimate["id"]

    update_response = client.patch(
        f"/api/v1/estimates/{estimate['id']}",
        json={"title": "Updated offer", "description": "Updated scope"},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated offer"
    assert update_response.json()["description"] == "Updated scope"

    archive_response = client.post(f"/api/v1/estimates/{estimate['id']}/archive", headers=headers)
    assert archive_response.status_code == 200
    assert archive_response.json()["status"] == "archived"
    assert archive_response.json()["archived_at"] is not None

    list_after_archive = client.get("/api/v1/estimates", headers=headers)
    assert list_after_archive.status_code == 200
    assert list_after_archive.json() == []


def test_estimate_status_transition_works(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    _, _, project = create_project_fixture(client, headers)
    estimate = create_estimate(client, headers, str(project["id"]))

    sent = set_estimate_status(client, headers, str(estimate["id"]), "sent")

    assert sent["status"] == "sent"
    revision = first_revision(client, headers, str(estimate["id"]))
    assert revision["status"] == "sent"
    assert revision["sent_at"] is not None


def test_estimate_revisions_are_preserved(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    _, _, project = create_project_fixture(client, headers)
    estimate = create_estimate(client, headers, str(project["id"]))
    revision = first_revision(client, headers, str(estimate["id"]))
    create_estimate_item(client, headers, str(revision["id"]), quantity=2, unit_price=500)

    set_estimate_status(client, headers, str(estimate["id"]), "sent")

    revisions_response = client.get(f"/api/v1/estimates/{estimate['id']}/revisions", headers=headers)
    assert revisions_response.status_code == 200
    revisions = revisions_response.json()
    assert [item["id"] for item in revisions] == [revision["id"]]
    assert revisions[0]["revision_number"] == 1
    assert_rounded(revisions[0]["total"], 1000.0)


def test_sent_or_accepted_revision_cannot_be_modified_directly(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    _, _, project = create_project_fixture(client, headers)
    estimate = create_estimate(client, headers, str(project["id"]))
    revision = first_revision(client, headers, str(estimate["id"]))
    item = create_estimate_item(client, headers, str(revision["id"]))

    set_estimate_status(client, headers, str(estimate["id"]), "sent")

    create_response = client.post(
        f"/api/v1/estimate-revisions/{revision['id']}/items",
        json={"item_type": "service", "name": "Extra work", "quantity": 1, "unit_price": 100},
        headers=headers,
    )
    assert create_response.status_code == 400

    update_response = client.patch(
        f"/api/v1/estimate-items/{item['id']}",
        json={"quantity": 2},
        headers=headers,
    )
    assert update_response.status_code == 400

    archive_response = client.post(f"/api/v1/estimate-items/{item['id']}/archive", headers=headers)
    assert archive_response.status_code == 400


def test_sent_estimate_metadata_cannot_be_overwritten(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    _, _, project = create_project_fixture(client, headers)
    estimate = create_estimate(client, headers, str(project["id"]))

    set_estimate_status(client, headers, str(estimate["id"]), "sent")

    response = client.patch(
        f"/api/v1/estimates/{estimate['id']}",
        json={"title": "Changed after sending"},
        headers=headers,
    )
    assert response.status_code == 400
    assert "ревизија" in response.json()["detail"]


def test_new_changes_after_sent_or_accepted_require_new_revision_behavior(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    _, _, project = create_project_fixture(client, headers)
    estimate = create_estimate(client, headers, str(project["id"]))
    revision = first_revision(client, headers, str(estimate["id"]))

    set_estimate_status(client, headers, str(estimate["id"]), "accepted")

    response = client.post(
        f"/api/v1/estimate-revisions/{revision['id']}/items",
        json={"item_type": "service", "name": "Late change", "quantity": 1, "unit_price": 100},
        headers=headers,
    )
    assert response.status_code == 400
    assert "ревизија" in response.json()["detail"]


def test_manual_estimate_item_create_list_update_archive(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    _, _, project = create_project_fixture(client, headers)
    estimate = create_estimate(client, headers, str(project["id"]))
    revision = first_revision(client, headers, str(estimate["id"]))

    item = create_estimate_item(client, headers, str(revision["id"]), quantity=2, unit_price=250)

    assert item["total_price"] == 500
    list_response = client.get(f"/api/v1/estimate-revisions/{revision['id']}/items", headers=headers)
    assert list_response.status_code == 200
    assert [line["id"] for line in list_response.json()] == [item["id"]]

    update_response = client.patch(
        f"/api/v1/estimate-items/{item['id']}",
        json={"quantity": 3, "unit_price": 300},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["quantity"] == 3
    assert update_response.json()["unit_price"] == 300
    assert update_response.json()["total_price"] == 900

    archive_response = client.post(f"/api/v1/estimate-items/{item['id']}/archive", headers=headers)
    assert archive_response.status_code == 200
    assert archive_response.json()["archived_at"] is not None

    list_after_archive = client.get(f"/api/v1/estimate-revisions/{revision['id']}/items", headers=headers)
    assert list_after_archive.status_code == 200
    assert list_after_archive.json() == []


def test_totals_calculate_correctly(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    _, _, project = create_project_fixture(client, headers)
    estimate = create_estimate(client, headers, str(project["id"]))
    revision = first_revision(client, headers, str(estimate["id"]))

    create_estimate_item(client, headers, str(revision["id"]), item_type="material", quantity=2, unit_price=100)
    create_estimate_item(client, headers, str(revision["id"]), item_type="labor", quantity=3, unit_price=50)

    detail_response = client.get(f"/api/v1/estimate-revisions/{revision['id']}", headers=headers)
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert_rounded(detail["subtotal"], 350.0)
    assert_rounded(detail["discount_total"], 0.0)
    assert_rounded(detail["adjustment_total"], 0.0)
    assert_rounded(detail["tax_total"], 0.0)
    assert_rounded(detail["total"], 350.0)


def test_discount_and_adjustment_affect_total_correctly(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    _, _, project = create_project_fixture(client, headers)
    estimate = create_estimate(client, headers, str(project["id"]))
    revision = first_revision(client, headers, str(estimate["id"]))

    create_estimate_item(client, headers, str(revision["id"]), item_type="service", quantity=1, unit_price=1000)
    create_estimate_item(client, headers, str(revision["id"]), item_type="discount", quantity=1, unit_price=100)
    create_estimate_item(client, headers, str(revision["id"]), item_type="adjustment", quantity=1, unit_price=50)

    detail_response = client.get(f"/api/v1/estimate-revisions/{revision['id']}", headers=headers)
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert_rounded(detail["subtotal"], 1000.0)
    assert_rounded(detail["discount_total"], 100.0)
    assert_rounded(detail["adjustment_total"], 50.0)
    assert_rounded(detail["total"], 950.0)


def test_create_estimate_from_completed_painting_calculation(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    project, _, calculation = completed_painting_run(client, headers)

    response = client.post(
        f"/api/v1/estimates/from-calculation/{calculation['id']}",
        json={"title": "Painting estimate"},
        headers=headers,
    )

    assert response.status_code == 201
    estimate = response.json()
    assert estimate["project_id"] == project["id"]
    assert estimate["source_calculation_run_id"] == calculation["id"]

    revision = first_revision(client, headers, str(estimate["id"]))
    items_response = client.get(f"/api/v1/estimate-revisions/{revision['id']}/items", headers=headers)
    assert items_response.status_code == 200
    items = items_response.json()
    assert [item["name"] for item in items] == ["Paint material", "Labor"]
    assert all(item["source_calculation_run_id"] == calculation["id"] for item in items)
    assert_rounded(revision["total"], calculation["output_payload"]["total_cost"])


def test_cannot_create_estimate_from_failed_calculation(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    _, _, project = create_project_fixture(client, headers)
    failed_calculation = run_painting(client, headers, project_id=str(project["id"]))
    assert failed_calculation["status"] == "failed"

    response = client.post(
        f"/api/v1/estimates/from-calculation/{failed_calculation['id']}",
        json={"title": "Invalid estimate"},
        headers=headers,
    )

    assert response.status_code == 400


def test_copied_calculation_line_items_preserve_historical_prices(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    _, paint, calculation = completed_painting_run(client, headers)
    response = client.post(
        f"/api/v1/estimates/from-calculation/{calculation['id']}",
        json={"title": "Historical estimate"},
        headers=headers,
    )
    assert response.status_code == 201
    revision = first_revision(client, headers, str(response.json()["id"]))
    items_response = client.get(f"/api/v1/estimate-revisions/{revision['id']}/items", headers=headers)
    assert items_response.status_code == 200
    paint_item = next(item for item in items_response.json() if item["material_id"] == paint["id"])
    original_total = paint_item["total_price"]

    update_material = client.patch(
        f"/api/v1/materials/{paint['id']}",
        json={"name": "Updated paint price metadata", "coverage_value": 8.0},
        headers=headers,
    )
    assert update_material.status_code == 200

    refreshed_items = client.get(f"/api/v1/estimate-revisions/{revision['id']}/items", headers=headers)
    assert refreshed_items.status_code == 200
    refreshed_paint_item = next(item for item in refreshed_items.json() if item["material_id"] == paint["id"])
    assert refreshed_paint_item["total_price"] == original_total


def test_tenant_isolation_for_estimates_revisions_and_items(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    owner = owner_headers(client, seeded_identity)
    other = other_headers(client, seeded_identity)
    _, _, other_project = create_project_fixture(client, other)
    other_estimate = create_estimate(client, other, str(other_project["id"]))
    other_revision = first_revision(client, other, str(other_estimate["id"]))
    other_item = create_estimate_item(client, other, str(other_revision["id"]))

    assert client.get(f"/api/v1/estimates/{other_estimate['id']}", headers=owner).status_code == 404
    assert (
        client.patch(
            f"/api/v1/estimates/{other_estimate['id']}",
            json={"title": "Cross tenant update"},
            headers=owner,
        ).status_code
        == 404
    )
    assert client.post(f"/api/v1/estimates/{other_estimate['id']}/archive", headers=owner).status_code == 404
    assert client.get(f"/api/v1/estimate-revisions/{other_revision['id']}", headers=owner).status_code == 404
    assert (
        client.post(
            f"/api/v1/estimate-revisions/{other_revision['id']}/items",
            json={"item_type": "service", "name": "Cross", "quantity": 1, "unit_price": 1},
            headers=owner,
        ).status_code
        == 404
    )
    assert client.patch(f"/api/v1/estimate-items/{other_item['id']}", json={"quantity": 2}, headers=owner).status_code == 404
    assert client.post(f"/api/v1/estimate-items/{other_item['id']}/archive", headers=owner).status_code == 404
    assert client.get("/api/v1/estimates", headers=owner).json() == []


def test_estimate_endpoints_require_authentication(client: TestClient) -> None:
    endpoints: list[tuple[str, str, dict[str, object] | None]] = [
        ("post", "/api/v1/estimates", {"project_id": "missing", "title": "Offer"}),
        ("get", "/api/v1/estimates", None),
        ("get", "/api/v1/estimates/missing", None),
        ("patch", "/api/v1/estimates/missing", {"title": "Updated"}),
        ("post", "/api/v1/estimates/missing/archive", None),
        ("post", "/api/v1/estimates/missing/status", {"status": "sent"}),
        ("post", "/api/v1/estimates/from-calculation/missing", {"title": "Offer"}),
        ("get", "/api/v1/estimates/missing/revisions", None),
        ("get", "/api/v1/estimate-revisions/missing", None),
        ("post", "/api/v1/estimate-revisions/missing/items", {"item_type": "service", "name": "Line"}),
        ("get", "/api/v1/estimate-revisions/missing/items", None),
        ("patch", "/api/v1/estimate-items/missing", {"quantity": 2}),
        ("post", "/api/v1/estimate-items/missing/archive", None),
    ]

    for method, path, payload in endpoints:
        response = getattr(client, method)(path, json=payload) if payload is not None else getattr(client, method)(path)
        assert response.status_code == 401
