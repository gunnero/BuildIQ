from collections.abc import Iterable
from typing import Optional

from fastapi.testclient import TestClient

from tests.test_customers_properties import (
    create_customer,
    create_property,
    other_headers,
    owner_headers,
)


def create_project(
    client: TestClient,
    headers: dict[str, str],
    customer_id: str,
    property_id: str,
    *,
    name: str = "Apartment renovation",
) -> dict[str, object]:
    response = client.post(
        "/api/v1/projects",
        json={
            "customer_id": customer_id,
            "property_id": property_id,
            "name": name,
            "description": "Full apartment renovation",
            "address": "Ilindenska 10",
            "start_date": "2026-07-20",
            "due_date": "2026-08-20",
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def create_task(
    client: TestClient,
    headers: dict[str, str],
    project_id: str,
    *,
    title: str = "Prepare site",
) -> dict[str, object]:
    response = client.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={
            "title": title,
            "description": "Protect floors and remove debris",
            "due_date": "2026-07-25",
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def create_project_fixture(
    client: TestClient,
    headers: dict[str, str],
) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    customer = create_customer(client, headers)
    property_item = create_property(client, headers, str(customer["id"]))
    project = create_project(client, headers, str(customer["id"]), str(property_item["id"]))
    return customer, property_item, project


def test_project_create_list_detail_update_archive(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    customer = create_customer(client, headers)
    property_item = create_property(client, headers, str(customer["id"]))

    created = create_project(client, headers, str(customer["id"]), str(property_item["id"]))

    assert created["company_id"] == seeded_identity["demo_company_id"]
    assert created["customer_id"] == customer["id"]
    assert created["property_id"] == property_item["id"]
    assert created["status"] == "draft"
    assert created["archived_at"] is None

    list_response = client.get("/api/v1/projects", headers=headers)
    assert list_response.status_code == 200
    assert [project["id"] for project in list_response.json()] == [created["id"]]

    detail_response = client.get(f"/api/v1/projects/{created['id']}", headers=headers)
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == created["id"]

    update_response = client.patch(
        f"/api/v1/projects/{created['id']}",
        json={"name": "Updated renovation", "description": "Updated scope"},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated renovation"
    assert update_response.json()["description"] == "Updated scope"

    archive_response = client.post(f"/api/v1/projects/{created['id']}/archive", headers=headers)
    assert archive_response.status_code == 200
    assert archive_response.json()["status"] == "archived"
    assert archive_response.json()["archived_at"] is not None

    list_after_archive = client.get("/api/v1/projects", headers=headers)
    assert list_after_archive.status_code == 200
    assert list_after_archive.json() == []


def test_project_creation_fails_when_customer_property_mismatch(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    customer_a = create_customer(client, headers, name="Customer A")
    property_a = create_property(client, headers, str(customer_a["id"]))
    customer_b = create_customer(client, headers, name="Customer B")

    response = client.post(
        "/api/v1/projects",
        json={
            "customer_id": customer_b["id"],
            "property_id": property_a["id"],
            "name": "Invalid project",
        },
        headers=headers,
    )

    assert response.status_code == 400


def test_project_status_change_creates_status_history(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    _, _, project = create_project_fixture(client, headers)

    response = client.post(
        f"/api/v1/projects/{project['id']}/status",
        json={"status": "active", "note": "Work started"},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "active"

    history_response = client.get(
        f"/api/v1/projects/{project['id']}/status-history",
        headers=headers,
    )
    assert history_response.status_code == 200
    history = history_response.json()
    assert len(history) == 1
    assert history[0]["from_status"] == "draft"
    assert history[0]["to_status"] == "active"
    assert history[0]["note"] == "Work started"


def test_project_timeline_events_are_created_for_create_update_status_archive(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    _, _, project = create_project_fixture(client, headers)

    client.patch(
        f"/api/v1/projects/{project['id']}",
        json={"name": "Timeline update"},
        headers=headers,
    )
    client.post(
        f"/api/v1/projects/{project['id']}/status",
        json={"status": "planned"},
        headers=headers,
    )
    client.post(f"/api/v1/projects/{project['id']}/archive", headers=headers)

    timeline_response = client.get(f"/api/v1/projects/{project['id']}/timeline", headers=headers)
    assert timeline_response.status_code == 200
    event_types = [event["event_type"] for event in timeline_response.json()]
    assert event_types == ["created", "updated", "status_changed", "archived"]


def test_task_create_list_detail_update_archive(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    _, _, project = create_project_fixture(client, headers)

    created = create_task(client, headers, str(project["id"]))

    assert created["company_id"] == seeded_identity["demo_company_id"]
    assert created["project_id"] == project["id"]
    assert created["status"] == "draft"
    assert created["archived_at"] is None

    list_response = client.get(f"/api/v1/projects/{project['id']}/tasks", headers=headers)
    assert list_response.status_code == 200
    assert [task["id"] for task in list_response.json()] == [created["id"]]

    detail_response = client.get(f"/api/v1/tasks/{created['id']}", headers=headers)
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == created["id"]

    update_response = client.patch(
        f"/api/v1/tasks/{created['id']}",
        json={"title": "Updated task", "description": "Updated description"},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated task"

    archive_response = client.post(f"/api/v1/tasks/{created['id']}/archive", headers=headers)
    assert archive_response.status_code == 200
    assert archive_response.json()["status"] == "archived"
    assert archive_response.json()["archived_at"] is not None

    list_after_archive = client.get(f"/api/v1/projects/{project['id']}/tasks", headers=headers)
    assert list_after_archive.status_code == 200
    assert list_after_archive.json() == []


def test_task_status_changes_work(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    _, _, project = create_project_fixture(client, headers)
    task = create_task(client, headers, str(project["id"]))

    response = client.post(
        f"/api/v1/tasks/{task['id']}/status",
        json={"status": "active"},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "active"


def test_tenant_isolation_for_projects_and_tasks(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    owner = owner_headers(client, seeded_identity)
    other = other_headers(client, seeded_identity)
    _, _, other_project = create_project_fixture(client, other)
    other_task = create_task(client, other, str(other_project["id"]))

    assert client.get(f"/api/v1/projects/{other_project['id']}", headers=owner).status_code == 404
    assert (
        client.patch(
            f"/api/v1/projects/{other_project['id']}",
            json={"name": "Cross tenant project update"},
            headers=owner,
        ).status_code
        == 404
    )
    assert client.post(f"/api/v1/projects/{other_project['id']}/archive", headers=owner).status_code == 404
    assert client.get(f"/api/v1/projects/{other_project['id']}/tasks", headers=owner).status_code == 404
    assert client.get(f"/api/v1/tasks/{other_task['id']}", headers=owner).status_code == 404
    assert (
        client.patch(
            f"/api/v1/tasks/{other_task['id']}",
            json={"title": "Cross tenant task update"},
            headers=owner,
        ).status_code
        == 404
    )
    assert client.post(f"/api/v1/tasks/{other_task['id']}/archive", headers=owner).status_code == 404

    project_list = client.get("/api/v1/projects", headers=owner)
    assert project_list.status_code == 200
    assert project_list.json() == []


def test_project_task_endpoints_require_authentication(client: TestClient) -> None:
    endpoints: Iterable[tuple[str, str, Optional[dict[str, str]]]] = [
        ("post", "/api/v1/projects", {"customer_id": "missing", "property_id": "missing", "name": "No Auth"}),
        ("get", "/api/v1/projects", None),
        ("get", "/api/v1/projects/missing", None),
        ("patch", "/api/v1/projects/missing", {"name": "No Auth"}),
        ("post", "/api/v1/projects/missing/archive", None),
        ("post", "/api/v1/projects/missing/status", {"status": "active"}),
        ("get", "/api/v1/projects/missing/status-history", None),
        ("get", "/api/v1/projects/missing/timeline", None),
        ("post", "/api/v1/projects/missing/tasks", {"title": "No Auth"}),
        ("get", "/api/v1/projects/missing/tasks", None),
        ("get", "/api/v1/tasks/missing", None),
        ("patch", "/api/v1/tasks/missing", {"title": "No Auth"}),
        ("post", "/api/v1/tasks/missing/archive", None),
        ("post", "/api/v1/tasks/missing/status", {"status": "active"}),
    ]

    for method, endpoint, payload in endpoints:
        request = getattr(client, method)
        response = request(endpoint, json=payload) if payload is not None else request(endpoint)
        assert response.status_code == 401, endpoint
