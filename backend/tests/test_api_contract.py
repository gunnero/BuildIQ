import json
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.kernel import AuditLog
from tests.test_customers_properties import owner_headers
from tests.test_estimates import create_estimate, set_estimate_status
from tests.test_payments_expenses import create_payment
from tests.test_projects_tasks import create_project_fixture


REQUIRED_OPENAPI_TAGS = {
    "health",
    "auth",
    "companies",
    "subscriptions",
    "customers",
    "properties",
    "projects",
    "tasks",
    "rooms",
    "measurements",
    "materials",
    "procurement",
    "calculations",
    "estimates",
    "payments",
    "expenses",
}


def test_openapi_contract_has_required_tags_and_operation_summaries(
    client: TestClient,
) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    schema = response.json()
    tags = {
        tag
        for path_item in schema["paths"].values()
        for operation in path_item.values()
        for tag in operation.get("tags", [])
    }
    assert REQUIRED_OPENAPI_TAGS.issubset(tags)

    operations_without_summary = [
        f"{method.upper()} {path}"
        for path, path_item in schema["paths"].items()
        for method, operation in path_item.items()
        if method.lower() in {"get", "post", "patch", "put", "delete"}
        and not operation.get("summary")
    ]
    assert operations_without_summary == []


def test_export_openapi_command_writes_contract_file(tmp_path: Path) -> None:
    from app.scripts.export_openapi import export_openapi_json

    output_path = tmp_path / "openapi.json"

    export_openapi_json(output_path)

    assert output_path.exists()
    schema = json.loads(output_path.read_text())
    assert schema["openapi"].startswith("3.")
    assert "/api/v1/auth/login" in schema["paths"]


def test_key_actions_create_audit_logs(
    client: TestClient,
    db_session: Session,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    login_logs = db_session.query(AuditLog).filter(AuditLog.action == "auth.login_success").all()
    assert len(login_logs) == 1
    assert login_logs[0].acting_user_id == seeded_identity["owner_user_id"]

    customer, _, project = create_project_fixture(client, headers)
    project_logs = db_session.query(AuditLog).filter(AuditLog.action == "project.created").all()
    assert len(project_logs) == 1
    assert project_logs[0].entity_id == project["id"]

    estimate = create_estimate(client, headers, str(project["id"]))
    set_estimate_status(client, headers, str(estimate["id"]), "sent")
    estimate_logs = (
        db_session.query(AuditLog)
        .filter(AuditLog.action == "estimate.status_changed")
        .all()
    )
    assert len(estimate_logs) == 1
    assert estimate_logs[0].entity_id == estimate["id"]
    assert estimate_logs[0].after_snapshot["status"] == "sent"

    payment = create_payment(
        client,
        headers,
        str(customer["id"]),
        str(project["id"]),
        amount=1000,
    )
    payment_logs = db_session.query(AuditLog).filter(AuditLog.action == "payment.created").all()
    assert len(payment_logs) == 1
    assert payment_logs[0].entity_id == payment["id"]
    assert payment_logs[0].after_snapshot["amount"] == 1000

    reverse_response = client.post(
        f"/api/v1/payments/{payment['id']}/reverse",
        json={"reason": "Wrong amount"},
        headers=headers,
    )
    assert reverse_response.status_code == 200
    reversal_logs = (
        db_session.query(AuditLog).filter(AuditLog.action == "payment.reversed").all()
    )
    assert len(reversal_logs) == 1
    assert reversal_logs[0].entity_id == payment["id"]
    assert reversal_logs[0].after_snapshot["status"] == "reversed"
