from typing import Optional

from fastapi.testclient import TestClient

from tests.test_customers_properties import other_headers, owner_headers
from tests.test_materials import material_unit_by_key
from tests.test_procurement import (
    create_material_price_override,
    create_price_book,
    create_price_book_item,
    create_supplier,
)
from tests.test_projects_tasks import create_project_fixture, create_task
from tests.test_rooms_measurements import (
    create_measurement_item,
    create_measurement_set,
    create_opening,
    create_room,
)


def create_paint_material(
    client: TestClient,
    headers: dict[str, str],
    *,
    name: str = "Interior paint",
    coverage_value: Optional[float] = 10.0,
    waste_percentage_default: Optional[float] = 5.0,
) -> dict[str, object]:
    unit = material_unit_by_key(client, headers, "liter")
    response = client.post(
        "/api/v1/materials",
        json={
            "name": name,
            "sku": "PAINT-001",
            "description": "Paint material",
            "unit_id": unit["id"],
            "coverage_value": coverage_value,
            "coverage_unit": "m2/liter" if coverage_value is not None else None,
            "package_quantity": 15.0,
            "waste_percentage_default": waste_percentage_default,
            "is_active": True,
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def run_painting(
    client: TestClient,
    headers: dict[str, str],
    *,
    project_id: str,
    room_id: Optional[str] = None,
    measurement_set_id: Optional[str] = None,
    input_payload: Optional[dict[str, object]] = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "engine_type": "painting",
        "project_id": project_id,
        "input_payload": input_payload or {},
    }
    if room_id is not None:
        payload["room_id"] = room_id
    if measurement_set_id is not None:
        payload["measurement_set_id"] = measurement_set_id
    response = client.post("/api/v1/calculations/run", json=payload, headers=headers)
    assert response.status_code == 201
    return response.json()


def assert_rounded(value: object, expected: float) -> None:
    assert round(float(value), 4) == round(expected, 4)


def test_painting_engine_appears_as_implemented(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)

    response = client.get("/api/v1/calculation-engines", headers=headers)

    assert response.status_code == 200
    painting = next(engine for engine in response.json() if engine["engine_type"] == "painting")
    assert painting["implemented"] is True
    assert painting["status"] == "implemented"


def test_valid_room_based_painting_run_completes_and_stores_line_items(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    _, _, project = create_project_fixture(client, headers)
    room = create_room(client, headers, str(project["id"]), length=5.0, width=4.0, height=3.0)
    paint = create_paint_material(client, headers, coverage_value=10.0)

    created = run_painting(
        client,
        headers,
        project_id=str(project["id"]),
        room_id=str(room["id"]),
        input_payload={
            "paint_material_id": paint["id"],
            "waste_percentage": 10,
            "labor_rate_per_m2": 120,
        },
    )

    assert created["status"] == "completed"
    assert created["engine_type"] == "painting"
    assert created["engine_version"] == "painting-1"
    output = created["output_payload"]
    assert_rounded(output["wall_area_net_m2"], 54.0)
    assert_rounded(output["ceiling_area_m2"], 20.0)
    assert_rounded(output["selected_area_m2"], 74.0)
    assert output["coats"] == 2
    assert output["waste_percentage"] == 10.0
    assert_rounded(output["paint_required_liters"], 16.28)
    assert output["primer_required_liters"] == 0.0
    assert output["paint_material_cost"] is None
    assert_rounded(output["labor_cost"], 8880.0)
    assert_rounded(output["total_cost"], 8880.0)
    assert output["warnings"] == ["Не е пронајдена цена за материјалот за боја."]
    assert len(created["line_items"]) == 2
    assert [item["name"] for item in created["line_items"]] == ["Боја", "Работна рака"]
    assert created["line_items"][0]["unit"] == "liter"
    assert_rounded(created["line_items"][0]["quantity"], 16.28)
    assert created["line_items"][0]["payload"]["material_id"] == paint["id"]
    assert created["line_items"][1]["unit"] == "m2"
    assert_rounded(created["line_items"][1]["payload"]["total_cost"], 8880.0)


def test_openings_reduce_wall_area_for_painting(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    _, _, project = create_project_fixture(client, headers)
    room = create_room(client, headers, str(project["id"]), length=5.0, width=4.0, height=3.0)
    create_opening(client, headers, str(room["id"]), width=1.0, height=2.0, quantity=1)

    created = run_painting(
        client,
        headers,
        project_id=str(project["id"]),
        room_id=str(room["id"]),
    )

    assert created["status"] == "completed"
    output = created["output_payload"]
    assert_rounded(output["wall_area_net_m2"], 52.0)
    assert_rounded(output["selected_area_m2"], 72.0)


def test_include_ceiling_false_excludes_ceiling(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    _, _, project = create_project_fixture(client, headers)
    room = create_room(client, headers, str(project["id"]), length=5.0, width=4.0, height=3.0)

    created = run_painting(
        client,
        headers,
        project_id=str(project["id"]),
        room_id=str(room["id"]),
        input_payload={"include_ceiling": False},
    )

    assert created["status"] == "completed"
    assert_rounded(created["output_payload"]["selected_area_m2"], 54.0)


def test_include_walls_false_excludes_walls(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    _, _, project = create_project_fixture(client, headers)
    room = create_room(client, headers, str(project["id"]), length=5.0, width=4.0, height=3.0)

    created = run_painting(
        client,
        headers,
        project_id=str(project["id"]),
        room_id=str(room["id"]),
        input_payload={"include_walls": False},
    )

    assert created["status"] == "completed"
    assert_rounded(created["output_payload"]["selected_area_m2"], 20.0)


def test_coats_and_waste_affect_liters(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    _, _, project = create_project_fixture(client, headers)
    room = create_room(client, headers, str(project["id"]), length=5.0, width=4.0, height=3.0)
    paint = create_paint_material(client, headers, coverage_value=10.0)

    created = run_painting(
        client,
        headers,
        project_id=str(project["id"]),
        room_id=str(room["id"]),
        input_payload={
            "paint_material_id": paint["id"],
            "coats": 3,
            "waste_percentage": 20,
        },
    )

    assert created["status"] == "completed"
    assert_rounded(created["output_payload"]["paint_required_liters"], 26.64)


def test_measurement_set_area_can_drive_painting_when_no_room_is_provided(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    _, _, project = create_project_fixture(client, headers)
    measurement_set = create_measurement_set(client, headers, str(project["id"]))
    create_measurement_item(client, headers, str(measurement_set["id"]), name="wall_area", unit="m2", quantity=40)
    create_measurement_item(client, headers, str(measurement_set["id"]), name="ceiling_area", unit="m2", quantity=12)

    created = run_painting(
        client,
        headers,
        project_id=str(project["id"]),
        measurement_set_id=str(measurement_set["id"]),
    )

    assert created["status"] == "completed"
    assert_rounded(created["output_payload"]["wall_area_net_m2"], 40.0)
    assert_rounded(created["output_payload"]["ceiling_area_m2"], 12.0)
    assert_rounded(created["output_payload"]["selected_area_m2"], 52.0)


def test_missing_area_fails_clearly(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    _, _, project = create_project_fixture(client, headers)

    created = run_painting(client, headers, project_id=str(project["id"]))

    assert created["status"] == "failed"
    assert created["output_payload"]["error_code"] == "painting_area_missing"
    assert created["output_payload"]["message"]


def test_missing_material_coverage_fails_clearly(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    _, _, project = create_project_fixture(client, headers)
    room = create_room(client, headers, str(project["id"]))
    paint = create_paint_material(client, headers, coverage_value=None)

    created = run_painting(
        client,
        headers,
        project_id=str(project["id"]),
        room_id=str(room["id"]),
        input_payload={"paint_material_id": paint["id"]},
    )

    assert created["status"] == "failed"
    assert created["output_payload"]["error_code"] == "material_coverage_missing"
    assert created["output_payload"]["material_id"] == paint["id"]


def test_material_price_is_resolved_using_procurement_rules(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    _, _, project = create_project_fixture(client, headers)
    room = create_room(client, headers, str(project["id"]), length=5.0, width=4.0, height=3.0)
    paint = create_paint_material(client, headers, coverage_value=10.0, waste_percentage_default=10.0)
    supplier = create_supplier(client, headers)
    price_book = create_price_book(client, headers, supplier_id=str(supplier["id"]), price_type="retail")
    item = create_price_book_item(
        client,
        headers,
        str(price_book["id"]),
        str(paint["id"]),
        supplier_id=str(supplier["id"]),
        unit_price=200.0,
    )

    created = run_painting(
        client,
        headers,
        project_id=str(project["id"]),
        room_id=str(room["id"]),
        input_payload={"paint_material_id": paint["id"]},
    )

    assert created["status"] == "completed"
    output = created["output_payload"]
    assert_rounded(output["paint_required_liters"], 16.28)
    assert_rounded(output["paint_material_cost"], 3256.0)
    assert_rounded(output["total_cost"], 3256.0)
    assert created["line_items"][0]["payload"]["price_source_type"] == "retail_price_book"
    assert created["line_items"][0]["payload"]["price_source_id"] == item["id"]


def test_project_override_price_beats_price_book_price(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
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
    override = create_material_price_override(
        client,
        headers,
        str(project["id"]),
        str(paint["id"]),
        supplier_id=str(supplier["id"]),
        unit_price=150.0,
    )

    created = run_painting(
        client,
        headers,
        project_id=str(project["id"]),
        room_id=str(room["id"]),
        input_payload={"paint_material_id": paint["id"]},
    )

    assert created["status"] == "completed"
    assert_rounded(created["output_payload"]["paint_material_cost"], 2442.0)
    assert created["line_items"][0]["payload"]["price_source_type"] == "project_override"
    assert created["line_items"][0]["payload"]["price_source_id"] == override["id"]


def test_labor_cost_calculates_correctly(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    _, _, project = create_project_fixture(client, headers)
    room = create_room(client, headers, str(project["id"]), length=5.0, width=4.0, height=3.0)

    created = run_painting(
        client,
        headers,
        project_id=str(project["id"]),
        room_id=str(room["id"]),
        input_payload={"labor_rate_per_m2": 100},
    )

    assert created["status"] == "completed"
    assert_rounded(created["output_payload"]["labor_cost"], 7400.0)
    assert_rounded(created["output_payload"]["total_cost"], 7400.0)
    assert created["line_items"][0]["name"] == "Работна рака"


def test_tenant_isolation_still_holds_for_painting_calculations(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    owner = owner_headers(client, seeded_identity)
    other = other_headers(client, seeded_identity)
    _, _, other_project = create_project_fixture(client, other)
    other_room = create_room(client, other, str(other_project["id"]))
    other_run = run_painting(
        client,
        other,
        project_id=str(other_project["id"]),
        room_id=str(other_room["id"]),
    )

    assert client.get(f"/api/v1/calculations/{other_run['id']}", headers=owner).status_code == 404
    assert client.post(f"/api/v1/calculations/{other_run['id']}/archive", headers=owner).status_code == 404
    assert client.get("/api/v1/calculations", headers=owner).json() == []


def test_non_painting_engines_remain_placeholder_not_implemented(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    _, _, project = create_project_fixture(client, headers)

    response = client.post(
        "/api/v1/calculations/run",
        json={
            "engine_type": "tiles",
            "project_id": project["id"],
            "input_payload": {"surface": "floor"},
        },
        headers=headers,
    )

    assert response.status_code == 201
    created = response.json()
    assert created["status"] == "failed"
    assert created["output_payload"]["error_code"] == "engine_not_implemented"
