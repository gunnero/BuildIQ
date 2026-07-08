from collections.abc import Iterable
from typing import Optional

from fastapi.testclient import TestClient

from tests.test_customers_properties import other_headers, owner_headers
from tests.test_projects_tasks import create_project_fixture, create_task
from tests.test_rooms_measurements import create_measurement_set, create_room


def run_calculation(
    client: TestClient,
    headers: dict[str, str],
    *,
    engine_type: str = "painting",
    project_id: Optional[str] = None,
    project_task_id: Optional[str] = None,
    room_id: Optional[str] = None,
    measurement_set_id: Optional[str] = None,
    input_payload: Optional[dict[str, object]] = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "engine_type": engine_type,
        "input_payload": input_payload or {"include_ceiling": True, "waste_percent": 10},
    }
    if project_id is not None:
        payload["project_id"] = project_id
    if project_task_id is not None:
        payload["project_task_id"] = project_task_id
    if room_id is not None:
        payload["room_id"] = room_id
    if measurement_set_id is not None:
        payload["measurement_set_id"] = measurement_set_id

    response = client.post("/api/v1/calculations/run", json=payload, headers=headers)
    assert response.status_code == 201
    return response.json()


def create_calculation_context(
    client: TestClient,
    headers: dict[str, str],
) -> tuple[dict[str, object], dict[str, object], dict[str, object], dict[str, object]]:
    _, _, project = create_project_fixture(client, headers)
    task = create_task(client, headers, str(project["id"]))
    room = create_room(client, headers, str(project["id"]), project_task_id=str(task["id"]))
    measurement_set = create_measurement_set(
        client,
        headers,
        str(project["id"]),
        project_task_id=str(task["id"]),
    )
    return project, task, room, measurement_set


def test_engine_registry_lists_placeholder_engines(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)

    response = client.get("/api/v1/calculation-engines", headers=headers)

    assert response.status_code == 200
    engines = response.json()
    assert {engine["engine_type"] for engine in engines} == {
        "painting",
        "tiles",
        "knauf",
        "flooring",
        "concrete",
        "facade",
    }
    assert all(engine["implemented"] is False for engine in engines)
    assert all(engine["status"] == "placeholder" for engine in engines)


def test_running_placeholder_engine_creates_failed_calculation_run_with_stored_input(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    project, task, room, measurement_set = create_calculation_context(client, headers)
    input_payload = {"include_ceiling": True, "surface": "walls"}

    created = run_calculation(
        client,
        headers,
        project_id=str(project["id"]),
        project_task_id=str(task["id"]),
        room_id=str(room["id"]),
        measurement_set_id=str(measurement_set["id"]),
        input_payload=input_payload,
    )

    assert created["company_id"] == seeded_identity["demo_company_id"]
    assert created["engine_type"] == "painting"
    assert created["engine_version"] == "placeholder-1"
    assert created["status"] == "failed"
    assert created["project_id"] == project["id"]
    assert created["project_task_id"] == task["id"]
    assert created["room_id"] == room["id"]
    assert created["measurement_set_id"] == measurement_set["id"]
    assert created["created_by_user_id"] == seeded_identity["owner_user_id"]
    assert created["input_payload"] == input_payload
    assert created["output_payload"]["error_code"] == "engine_not_implemented"
    assert "not implemented" in created["output_payload"]["message"]
    assert created["line_items"] == []


def test_calculation_list_detail_and_archive_work(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    project, task, room, measurement_set = create_calculation_context(client, headers)
    created = run_calculation(
        client,
        headers,
        engine_type="flooring",
        project_id=str(project["id"]),
        project_task_id=str(task["id"]),
        room_id=str(room["id"]),
        measurement_set_id=str(measurement_set["id"]),
    )

    list_response = client.get("/api/v1/calculations", headers=headers)
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [created["id"]]

    detail_response = client.get(f"/api/v1/calculations/{created['id']}", headers=headers)
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == created["id"]

    archive_response = client.post(f"/api/v1/calculations/{created['id']}/archive", headers=headers)
    assert archive_response.status_code == 200
    assert archive_response.json()["status"] == "archived"
    assert archive_response.json()["input_payload"] == created["input_payload"]

    detail_after_archive = client.get(f"/api/v1/calculations/{created['id']}", headers=headers)
    assert detail_after_archive.status_code == 200
    assert detail_after_archive.json()["status"] == "archived"


def test_tenant_isolation_for_calculation_runs(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    owner = owner_headers(client, seeded_identity)
    other = other_headers(client, seeded_identity)
    project, task, room, measurement_set = create_calculation_context(client, other)
    other_run = run_calculation(
        client,
        other,
        project_id=str(project["id"]),
        project_task_id=str(task["id"]),
        room_id=str(room["id"]),
        measurement_set_id=str(measurement_set["id"]),
    )

    assert client.get(f"/api/v1/calculations/{other_run['id']}", headers=owner).status_code == 404
    assert client.post(f"/api/v1/calculations/{other_run['id']}/archive", headers=owner).status_code == 404

    list_response = client.get("/api/v1/calculations", headers=owner)
    assert list_response.status_code == 200
    assert list_response.json() == []


def test_invalid_project_task_room_and_measurement_set_links_are_rejected(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    project_a, task_a, room_a, measurement_set_a = create_calculation_context(client, headers)
    project_b, _, _, _ = create_calculation_context(client, headers)

    task_mismatch = client.post(
        "/api/v1/calculations/run",
        json={
            "engine_type": "painting",
            "project_id": project_b["id"],
            "project_task_id": task_a["id"],
            "input_payload": {"scope": "task mismatch"},
        },
        headers=headers,
    )
    assert task_mismatch.status_code == 400

    room_mismatch = client.post(
        "/api/v1/calculations/run",
        json={
            "engine_type": "painting",
            "project_id": project_b["id"],
            "room_id": room_a["id"],
            "input_payload": {"scope": "room mismatch"},
        },
        headers=headers,
    )
    assert room_mismatch.status_code == 400

    measurement_set_mismatch = client.post(
        "/api/v1/calculations/run",
        json={
            "engine_type": "painting",
            "project_id": project_b["id"],
            "measurement_set_id": measurement_set_a["id"],
            "input_payload": {"scope": "measurement set mismatch"},
        },
        headers=headers,
    )
    assert measurement_set_mismatch.status_code == 400

    missing_project = client.post(
        "/api/v1/calculations/run",
        json={
            "engine_type": "painting",
            "project_task_id": task_a["id"],
            "input_payload": {"scope": "missing project"},
        },
        headers=headers,
    )
    assert missing_project.status_code == 400

    assert project_a["id"] != project_b["id"]


def test_calculation_run_is_immutable_after_creation_except_archive_status(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    project, _, _, _ = create_calculation_context(client, headers)
    created = run_calculation(
        client,
        headers,
        project_id=str(project["id"]),
        input_payload={"first": True},
    )

    patch_response = client.patch(
        f"/api/v1/calculations/{created['id']}",
        json={"input_payload": {"first": False}, "status": "completed"},
        headers=headers,
    )
    assert patch_response.status_code == 405

    second = run_calculation(
        client,
        headers,
        project_id=str(project["id"]),
        input_payload={"first": False},
    )
    assert second["id"] != created["id"]

    original_detail = client.get(f"/api/v1/calculations/{created['id']}", headers=headers)
    assert original_detail.status_code == 200
    assert original_detail.json()["input_payload"] == {"first": True}
    assert original_detail.json()["status"] == "failed"


def test_calculation_endpoints_require_authentication(client: TestClient) -> None:
    endpoints: Iterable[tuple[str, str, Optional[dict[str, object]]]] = [
        ("post", "/api/v1/calculations/run", {"engine_type": "painting", "input_payload": {}}),
        ("get", "/api/v1/calculations", None),
        ("get", "/api/v1/calculations/missing", None),
        ("post", "/api/v1/calculations/missing/archive", None),
        ("get", "/api/v1/calculation-engines", None),
    ]

    for method, endpoint, payload in endpoints:
        request = getattr(client, method)
        response = request(endpoint, json=payload) if payload is not None else request(endpoint)
        assert response.status_code == 401, endpoint
