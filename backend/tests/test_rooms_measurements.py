from collections.abc import Iterable
from typing import Optional

import pytest
from fastapi.testclient import TestClient

from tests.test_customers_properties import other_headers, owner_headers
from tests.test_projects_tasks import create_project_fixture, create_task


def create_room(
    client: TestClient,
    headers: dict[str, str],
    project_id: str,
    *,
    name: str = "Living room",
    room_type: str = "living_room",
    project_task_id: Optional[str] = None,
    length: float = 5.0,
    width: float = 4.0,
    height: float = 3.0,
) -> dict[str, object]:
    response = client.post(
        f"/api/v1/projects/{project_id}/rooms",
        json={
            "name": name,
            "room_type": room_type,
            "project_task_id": project_task_id,
            "floor": "1",
            "note": "Room note",
            "length": length,
            "width": width,
            "height": height,
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def create_opening(
    client: TestClient,
    headers: dict[str, str],
    room_id: str,
    *,
    opening_type: str = "door",
    name: str = "Main door",
    width: float = 1.0,
    height: float = 2.0,
    quantity: int = 1,
) -> dict[str, object]:
    response = client.post(
        f"/api/v1/rooms/{room_id}/openings",
        json={
            "opening_type": opening_type,
            "name": name,
            "width": width,
            "height": height,
            "quantity": quantity,
            "note": "Opening note",
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def create_measurement_set(
    client: TestClient,
    headers: dict[str, str],
    project_id: str,
    *,
    name: str = "Initial measurements",
    project_task_id: Optional[str] = None,
) -> dict[str, object]:
    response = client.post(
        f"/api/v1/projects/{project_id}/measurement-sets",
        json={
            "name": name,
            "description": "Measurements before calculations",
            "project_task_id": project_task_id,
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def create_measurement_item(
    client: TestClient,
    headers: dict[str, str],
    measurement_set_id: str,
    *,
    name: str = "Skirting length",
    unit: str = "m",
    quantity: float = 18.0,
) -> dict[str, object]:
    response = client.post(
        f"/api/v1/measurement-sets/{measurement_set_id}/items",
        json={
            "name": name,
            "unit": unit,
            "quantity": quantity,
            "note": "Measured on site",
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def test_room_create_list_detail_update_archive(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    _, _, project = create_project_fixture(client, headers)

    created = create_room(client, headers, str(project["id"]))

    assert created["company_id"] == seeded_identity["demo_company_id"]
    assert created["project_id"] == project["id"]
    assert created["room_type"] == "living_room"
    assert created["archived_at"] is None

    list_response = client.get(f"/api/v1/projects/{project['id']}/rooms", headers=headers)
    assert list_response.status_code == 200
    assert [room["id"] for room in list_response.json()] == [created["id"]]

    detail_response = client.get(f"/api/v1/rooms/{created['id']}", headers=headers)
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == created["id"]

    update_response = client.patch(
        f"/api/v1/rooms/{created['id']}",
        json={"name": "Updated living room", "room_type": "room", "height": 2.8},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated living room"
    assert update_response.json()["room_type"] == "room"
    assert update_response.json()["height"] == 2.8

    archive_response = client.post(f"/api/v1/rooms/{created['id']}/archive", headers=headers)
    assert archive_response.status_code == 200
    assert archive_response.json()["archived_at"] is not None

    list_after_archive = client.get(f"/api/v1/projects/{project['id']}/rooms", headers=headers)
    assert list_after_archive.status_code == 200
    assert list_after_archive.json() == []


def test_room_computed_areas_are_correct(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    _, _, project = create_project_fixture(client, headers)
    room = create_room(client, headers, str(project["id"]), length=5.0, width=4.0, height=3.0)

    detail_response = client.get(f"/api/v1/rooms/{room['id']}", headers=headers)

    assert detail_response.status_code == 200
    data = detail_response.json()
    assert data["floor_area"] == 20.0
    assert data["ceiling_area"] == 20.0
    assert data["wall_area_gross"] == 54.0
    assert data["openings_area_total"] == 0.0
    assert data["wall_area_net"] == 54.0
    assert data["total_paintable_area"] == 74.0


def test_openings_reduce_wall_area_net(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    _, _, project = create_project_fixture(client, headers)
    room = create_room(client, headers, str(project["id"]), length=5.0, width=4.0, height=3.0)

    opening = create_opening(client, headers, str(room["id"]), width=1.0, height=2.0, quantity=1)

    list_response = client.get(f"/api/v1/rooms/{room['id']}/openings", headers=headers)
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [opening["id"]]

    detail_response = client.get(f"/api/v1/rooms/{room['id']}", headers=headers)
    assert detail_response.status_code == 200
    data = detail_response.json()
    assert data["openings_area_total"] == 2.0
    assert data["wall_area_net"] == 52.0
    assert data["total_paintable_area"] == 72.0

    update_response = client.patch(
        f"/api/v1/openings/{opening['id']}",
        json={"width": 1.2, "quantity": 2},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["width"] == 1.2
    assert update_response.json()["quantity"] == 2

    archive_response = client.post(f"/api/v1/openings/{opening['id']}/archive", headers=headers)
    assert archive_response.status_code == 200
    assert archive_response.json()["archived_at"] is not None

    list_after_archive = client.get(f"/api/v1/rooms/{room['id']}/openings", headers=headers)
    assert list_after_archive.status_code == 200
    assert list_after_archive.json() == []


def test_multiple_openings_with_quantity_are_calculated_correctly(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    _, _, project = create_project_fixture(client, headers)
    room = create_room(client, headers, str(project["id"]), length=5.0, width=4.0, height=2.8)

    create_opening(client, headers, str(room["id"]), opening_type="door", width=0.9, height=2.1, quantity=1)
    create_opening(
        client,
        headers,
        str(room["id"]),
        opening_type="window",
        name="Window",
        width=1.2,
        height=1.0,
        quantity=2,
    )

    detail_response = client.get(f"/api/v1/rooms/{room['id']}", headers=headers)

    assert detail_response.status_code == 200
    data = detail_response.json()
    assert data["wall_area_gross"] == pytest.approx(50.4)
    assert data["openings_area_total"] == pytest.approx(4.29)
    assert data["wall_area_net"] == pytest.approx(46.11)
    assert data["total_paintable_area"] == pytest.approx(66.11)


def test_room_project_task_must_belong_to_same_project_and_company(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    _, _, project_a = create_project_fixture(client, headers)
    _, _, project_b = create_project_fixture(client, headers)
    task = create_task(client, headers, str(project_a["id"]))

    valid_room = create_room(
        client,
        headers,
        str(project_a["id"]),
        project_task_id=str(task["id"]),
    )
    assert valid_room["project_task_id"] == task["id"]

    mismatch_response = client.post(
        f"/api/v1/projects/{project_b['id']}/rooms",
        json={
            "name": "Mismatched task room",
            "room_type": "room",
            "project_task_id": task["id"],
            "length": 4.0,
            "width": 3.0,
            "height": 2.7,
        },
        headers=headers,
    )
    assert mismatch_response.status_code == 400


def test_measurement_set_create_list_detail(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    _, _, project = create_project_fixture(client, headers)

    created = create_measurement_set(client, headers, str(project["id"]))

    assert created["company_id"] == seeded_identity["demo_company_id"]
    assert created["project_id"] == project["id"]
    assert created["archived_at"] is None

    list_response = client.get(f"/api/v1/projects/{project['id']}/measurement-sets", headers=headers)
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [created["id"]]

    detail_response = client.get(f"/api/v1/measurement-sets/{created['id']}", headers=headers)
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == created["id"]


def test_measurement_item_create_list_update_archive(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    _, _, project = create_project_fixture(client, headers)
    measurement_set = create_measurement_set(client, headers, str(project["id"]))

    created = create_measurement_item(client, headers, str(measurement_set["id"]))

    assert created["company_id"] == seeded_identity["demo_company_id"]
    assert created["measurement_set_id"] == measurement_set["id"]
    assert created["unit"] == "m"
    assert created["quantity"] == 18.0

    list_response = client.get(f"/api/v1/measurement-sets/{measurement_set['id']}/items", headers=headers)
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [created["id"]]

    update_response = client.patch(
        f"/api/v1/measurement-items/{created['id']}",
        json={"name": "Updated skirting", "unit": "piece", "quantity": 12},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated skirting"
    assert update_response.json()["unit"] == "piece"
    assert update_response.json()["quantity"] == 12.0

    archive_response = client.post(f"/api/v1/measurement-items/{created['id']}/archive", headers=headers)
    assert archive_response.status_code == 200
    assert archive_response.json()["archived_at"] is not None

    list_after_archive = client.get(f"/api/v1/measurement-sets/{measurement_set['id']}/items", headers=headers)
    assert list_after_archive.status_code == 200
    assert list_after_archive.json() == []


def test_tenant_isolation_for_rooms_openings_measurement_sets_and_items(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    owner = owner_headers(client, seeded_identity)
    other = other_headers(client, seeded_identity)
    _, _, other_project = create_project_fixture(client, other)
    other_room = create_room(client, other, str(other_project["id"]))
    other_opening = create_opening(client, other, str(other_room["id"]))
    other_set = create_measurement_set(client, other, str(other_project["id"]))
    other_item = create_measurement_item(client, other, str(other_set["id"]))

    assert client.get(f"/api/v1/projects/{other_project['id']}/rooms", headers=owner).status_code == 404
    assert client.get(f"/api/v1/rooms/{other_room['id']}", headers=owner).status_code == 404
    assert (
        client.patch(
            f"/api/v1/rooms/{other_room['id']}",
            json={"name": "Cross tenant room update"},
            headers=owner,
        ).status_code
        == 404
    )
    assert client.post(f"/api/v1/rooms/{other_room['id']}/archive", headers=owner).status_code == 404
    assert client.get(f"/api/v1/rooms/{other_room['id']}/openings", headers=owner).status_code == 404
    assert (
        client.patch(
            f"/api/v1/openings/{other_opening['id']}",
            json={"name": "Cross tenant opening update"},
            headers=owner,
        ).status_code
        == 404
    )
    assert client.post(f"/api/v1/openings/{other_opening['id']}/archive", headers=owner).status_code == 404

    assert client.get(f"/api/v1/projects/{other_project['id']}/measurement-sets", headers=owner).status_code == 404
    assert client.get(f"/api/v1/measurement-sets/{other_set['id']}", headers=owner).status_code == 404
    assert client.get(f"/api/v1/measurement-sets/{other_set['id']}/items", headers=owner).status_code == 404
    assert (
        client.patch(
            f"/api/v1/measurement-items/{other_item['id']}",
            json={"name": "Cross tenant item update"},
            headers=owner,
        ).status_code
        == 404
    )
    assert client.post(f"/api/v1/measurement-items/{other_item['id']}/archive", headers=owner).status_code == 404


def test_room_measurement_endpoints_require_authentication(client: TestClient) -> None:
    endpoints: Iterable[tuple[str, str, Optional[dict[str, object]]]] = [
        (
            "post",
            "/api/v1/projects/missing/rooms",
            {"name": "No Auth", "room_type": "room", "length": 1, "width": 1, "height": 1},
        ),
        ("get", "/api/v1/projects/missing/rooms", None),
        ("get", "/api/v1/rooms/missing", None),
        ("patch", "/api/v1/rooms/missing", {"name": "No Auth"}),
        ("post", "/api/v1/rooms/missing/archive", None),
        (
            "post",
            "/api/v1/rooms/missing/openings",
            {"opening_type": "door", "name": "No Auth", "width": 1, "height": 2, "quantity": 1},
        ),
        ("get", "/api/v1/rooms/missing/openings", None),
        ("patch", "/api/v1/openings/missing", {"name": "No Auth"}),
        ("post", "/api/v1/openings/missing/archive", None),
        ("post", "/api/v1/projects/missing/measurement-sets", {"name": "No Auth"}),
        ("get", "/api/v1/projects/missing/measurement-sets", None),
        ("get", "/api/v1/measurement-sets/missing", None),
        ("post", "/api/v1/measurement-sets/missing/items", {"name": "No Auth", "unit": "m", "quantity": 1}),
        ("get", "/api/v1/measurement-sets/missing/items", None),
        ("patch", "/api/v1/measurement-items/missing", {"name": "No Auth"}),
        ("post", "/api/v1/measurement-items/missing/archive", None),
    ]

    for method, endpoint, payload in endpoints:
        request = getattr(client, method)
        response = request(endpoint, json=payload) if payload is not None else request(endpoint)
        assert response.status_code == 401, endpoint
