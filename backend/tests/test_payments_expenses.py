from typing import Optional

from fastapi.testclient import TestClient

from tests.test_customers_properties import other_headers, owner_headers
from tests.test_estimates import (
    create_estimate,
    create_estimate_item,
    first_revision,
    set_estimate_status,
)
from tests.test_materials import create_material
from tests.test_procurement import create_supplier
from tests.test_projects_tasks import create_project_fixture


def assert_rounded(value: object, expected: float) -> None:
    assert round(float(value), 4) == round(expected, 4)


def set_project_agreed_price(
    client: TestClient,
    headers: dict[str, str],
    project_id: str,
    amount: float,
) -> dict[str, object]:
    response = client.patch(
        f"/api/v1/projects/{project_id}",
        json={"agreed_project_price": amount},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["agreed_project_price"] == amount
    return response.json()


def create_accepted_estimate(
    client: TestClient,
    headers: dict[str, str],
    project_id: str,
    *,
    total: float = 40000.0,
) -> tuple[dict[str, object], dict[str, object]]:
    estimate = create_estimate(client, headers, project_id)
    revision = first_revision(client, headers, str(estimate["id"]))
    create_estimate_item(
        client,
        headers,
        str(revision["id"]),
        item_type="service",
        name="Accepted scope",
        quantity=1,
        unit_price=total,
    )
    set_estimate_status(client, headers, str(estimate["id"]), "accepted")
    refreshed_revision = first_revision(client, headers, str(estimate["id"]))
    return estimate, refreshed_revision


def create_payment(
    client: TestClient,
    headers: dict[str, str],
    customer_id: str,
    project_id: str,
    *,
    estimate_id: Optional[str] = None,
    amount: float = 20000.0,
    status: str = "received",
    payment_method: str = "bank_transfer",
    note: str = "Advance payment",
) -> dict[str, object]:
    response = client.post(
        "/api/v1/payments",
        json={
            "customer_id": customer_id,
            "project_id": project_id,
            "estimate_id": estimate_id,
            "amount": amount,
            "payment_method": payment_method,
            "payment_date": "2026-07-08",
            "status": status,
            "note": note,
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def create_expense_category(
    client: TestClient,
    headers: dict[str, str],
    *,
    name: str = "Materials",
) -> dict[str, object]:
    response = client.post(
        "/api/v1/expense-categories",
        json={"name": name, "description": "Project cost category"},
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def create_expense(
    client: TestClient,
    headers: dict[str, str],
    *,
    project_id: Optional[str] = None,
    category_id: Optional[str] = None,
    supplier_id: Optional[str] = None,
    material_id: Optional[str] = None,
    amount: float = 15000.0,
    status: str = "recorded",
) -> dict[str, object]:
    response = client.post(
        "/api/v1/expenses",
        json={
            "project_id": project_id,
            "category_id": category_id,
            "supplier_id": supplier_id,
            "material_id": material_id,
            "description": "Paint and supplies",
            "amount": amount,
            "expense_date": "2026-07-08",
            "payment_method": "cash",
            "status": status,
            "note": "Receipt recorded",
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def test_payment_create_list_detail(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    customer, _, project = create_project_fixture(client, headers)
    estimate, _ = create_accepted_estimate(client, headers, str(project["id"]), total=40000)

    payment = create_payment(
        client,
        headers,
        str(customer["id"]),
        str(project["id"]),
        estimate_id=str(estimate["id"]),
        amount=20000,
    )

    assert payment["company_id"] == seeded_identity["demo_company_id"]
    assert payment["customer_id"] == customer["id"]
    assert payment["project_id"] == project["id"]
    assert payment["estimate_id"] == estimate["id"]
    assert payment["payment_method"] == "bank_transfer"
    assert payment["status"] == "received"
    assert payment["created_by_user_id"] == seeded_identity["owner_user_id"]
    assert len(payment["allocations"]) == 1
    assert payment["allocations"][0]["estimate_id"] == estimate["id"]
    assert_rounded(payment["allocations"][0]["amount"], 20000)

    list_response = client.get("/api/v1/payments", headers=headers)
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [payment["id"]]

    detail_response = client.get(f"/api/v1/payments/{payment['id']}", headers=headers)
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == payment["id"]


def test_payment_amount_must_be_positive(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    customer, _, project = create_project_fixture(client, headers)

    response = client.post(
        "/api/v1/payments",
        json={
            "customer_id": customer["id"],
            "project_id": project["id"],
            "amount": 0,
            "payment_method": "cash",
            "payment_date": "2026-07-08",
        },
        headers=headers,
    )

    assert response.status_code == 400


def test_payment_reverse_changes_status_and_preserves_record(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    customer, _, project = create_project_fixture(client, headers)
    payment = create_payment(client, headers, str(customer["id"]), str(project["id"]))

    response = client.post(
        f"/api/v1/payments/{payment['id']}/reverse",
        json={"reason": "Customer payment returned"},
        headers=headers,
    )

    assert response.status_code == 200
    reversed_payment = response.json()
    assert reversed_payment["status"] == "reversed"
    assert reversed_payment["reversal_reason"] == "Customer payment returned"
    assert reversed_payment["reversed_at"] is not None
    assert reversed_payment["reversed_by_user_id"] == seeded_identity["owner_user_id"]

    detail_response = client.get(f"/api/v1/payments/{payment['id']}", headers=headers)
    assert detail_response.status_code == 200
    assert detail_response.json()["status"] == "reversed"


def test_archived_payment_excluded_from_active_summary(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    customer, _, project = create_project_fixture(client, headers)
    set_project_agreed_price(client, headers, str(project["id"]), 40000)
    payment = create_payment(client, headers, str(customer["id"]), str(project["id"]), amount=20000)

    archive_response = client.post(f"/api/v1/payments/{payment['id']}/archive", headers=headers)
    assert archive_response.status_code == 200
    assert archive_response.json()["status"] == "archived"

    summary_response = client.get(f"/api/v1/projects/{project['id']}/financial-summary", headers=headers)
    assert summary_response.status_code == 200
    summary = summary_response.json()
    assert_rounded(summary["total_received_payments"], 0.0)
    assert_rounded(summary["outstanding_balance"], 40000.0)


def test_project_financial_summary_uses_accepted_estimate_total_first(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    customer, _, project = create_project_fixture(client, headers)
    set_project_agreed_price(client, headers, str(project["id"]), 50000)
    create_accepted_estimate(client, headers, str(project["id"]), total=40000)
    create_payment(client, headers, str(customer["id"]), str(project["id"]), amount=20000)

    response = client.get(f"/api/v1/projects/{project['id']}/financial-summary", headers=headers)

    assert response.status_code == 200
    summary = response.json()
    assert summary["project_id"] == project["id"]
    assert summary["customer_id"] == customer["id"]
    assert_rounded(summary["accepted_estimate_total"], 40000.0)
    assert_rounded(summary["agreed_project_price"], 50000.0)
    assert summary["revenue_basis"] == "accepted_estimate"
    assert_rounded(summary["total_received_payments"], 20000.0)
    assert_rounded(summary["outstanding_balance"], 20000.0)
    assert summary["payment_status"] == "partially_paid"


def test_project_financial_summary_falls_back_to_agreed_project_price(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    customer, _, project = create_project_fixture(client, headers)
    set_project_agreed_price(client, headers, str(project["id"]), 40000)
    create_payment(client, headers, str(customer["id"]), str(project["id"]), amount=20000)

    response = client.get(f"/api/v1/projects/{project['id']}/financial-summary", headers=headers)

    assert response.status_code == 200
    summary = response.json()
    assert summary["accepted_estimate_total"] is None
    assert_rounded(summary["agreed_project_price"], 40000.0)
    assert summary["revenue_basis"] == "agreed_project_price"
    assert_rounded(summary["outstanding_balance"], 20000.0)
    assert summary["payment_status"] == "partially_paid"


def test_partial_paid_and_overpaid_statuses_calculate_correctly(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    customer, _, project = create_project_fixture(client, headers)
    set_project_agreed_price(client, headers, str(project["id"]), 1000)

    unpaid = client.get(f"/api/v1/projects/{project['id']}/financial-summary", headers=headers).json()
    assert unpaid["payment_status"] == "unpaid"

    create_payment(client, headers, str(customer["id"]), str(project["id"]), amount=500)
    partial = client.get(f"/api/v1/projects/{project['id']}/financial-summary", headers=headers).json()
    assert partial["payment_status"] == "partially_paid"

    create_payment(client, headers, str(customer["id"]), str(project["id"]), amount=500)
    paid = client.get(f"/api/v1/projects/{project['id']}/financial-summary", headers=headers).json()
    assert paid["payment_status"] == "paid"

    create_payment(client, headers, str(customer["id"]), str(project["id"]), amount=100)
    overpaid = client.get(f"/api/v1/projects/{project['id']}/financial-summary", headers=headers).json()
    assert overpaid["payment_status"] == "overpaid"
    assert_rounded(overpaid["outstanding_balance"], -100.0)


def test_expense_category_create_list_update_archive(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)

    category = create_expense_category(client, headers)

    assert category["company_id"] == seeded_identity["demo_company_id"]
    assert category["name"] == "Materials"
    assert category["archived_at"] is None

    list_response = client.get("/api/v1/expense-categories", headers=headers)
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [category["id"]]

    update_response = client.patch(
        f"/api/v1/expense-categories/{category['id']}",
        json={"name": "Labor", "description": "Updated category"},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Labor"

    archive_response = client.post(f"/api/v1/expense-categories/{category['id']}/archive", headers=headers)
    assert archive_response.status_code == 200
    assert archive_response.json()["archived_at"] is not None

    list_after_archive = client.get("/api/v1/expense-categories", headers=headers)
    assert list_after_archive.status_code == 200
    assert list_after_archive.json() == []


def test_expense_create_list_detail_reverse_archive(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    _, _, project = create_project_fixture(client, headers)
    category = create_expense_category(client, headers)
    supplier = create_supplier(client, headers)
    material = create_material(client, headers)

    expense = create_expense(
        client,
        headers,
        project_id=str(project["id"]),
        category_id=str(category["id"]),
        supplier_id=str(supplier["id"]),
        material_id=str(material["id"]),
        amount=12000,
    )

    assert expense["company_id"] == seeded_identity["demo_company_id"]
    assert expense["project_id"] == project["id"]
    assert expense["category_id"] == category["id"]
    assert expense["supplier_id"] == supplier["id"]
    assert expense["material_id"] == material["id"]
    assert expense["status"] == "recorded"

    list_response = client.get("/api/v1/expenses", headers=headers)
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [expense["id"]]

    detail_response = client.get(f"/api/v1/expenses/{expense['id']}", headers=headers)
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == expense["id"]

    reverse_response = client.post(
        f"/api/v1/expenses/{expense['id']}/reverse",
        json={"reason": "Duplicate receipt"},
        headers=headers,
    )
    assert reverse_response.status_code == 200
    assert reverse_response.json()["status"] == "reversed"
    assert reverse_response.json()["reversal_reason"] == "Duplicate receipt"

    archive_response = client.post(f"/api/v1/expenses/{expense['id']}/archive", headers=headers)
    assert archive_response.status_code == 200
    assert archive_response.json()["status"] == "archived"

    list_after_archive = client.get("/api/v1/expenses", headers=headers)
    assert list_after_archive.status_code == 200
    assert list_after_archive.json() == []


def test_expense_amount_must_be_positive(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)

    response = client.post(
        "/api/v1/expenses",
        json={
            "description": "Invalid cost",
            "amount": 0,
            "expense_date": "2026-07-08",
            "payment_method": "cash",
        },
        headers=headers,
    )

    assert response.status_code == 400


def test_project_expenses_affect_estimated_profit(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    headers = owner_headers(client, seeded_identity)
    _, _, project = create_project_fixture(client, headers)
    create_accepted_estimate(client, headers, str(project["id"]), total=40000)
    category = create_expense_category(client, headers)
    create_expense(client, headers, project_id=str(project["id"]), category_id=str(category["id"]), amount=15000)

    response = client.get(f"/api/v1/projects/{project['id']}/financial-summary", headers=headers)

    assert response.status_code == 200
    summary = response.json()
    assert_rounded(summary["accepted_estimate_total"], 40000.0)
    assert_rounded(summary["total_recorded_expenses"], 15000.0)
    assert_rounded(summary["estimated_profit"], 25000.0)


def test_tenant_isolation_for_payments_allocations_expenses_and_categories(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    owner = owner_headers(client, seeded_identity)
    other = other_headers(client, seeded_identity)
    other_customer, _, other_project = create_project_fixture(client, other)
    other_payment = create_payment(client, other, str(other_customer["id"]), str(other_project["id"]))
    other_category = create_expense_category(client, other)
    other_expense = create_expense(
        client,
        other,
        project_id=str(other_project["id"]),
        category_id=str(other_category["id"]),
    )

    assert client.get(f"/api/v1/payments/{other_payment['id']}", headers=owner).status_code == 404
    assert client.post(f"/api/v1/payments/{other_payment['id']}/reverse", json={"reason": "Cross"}, headers=owner).status_code == 404
    assert client.post(f"/api/v1/payments/{other_payment['id']}/archive", headers=owner).status_code == 404
    assert client.get(f"/api/v1/expenses/{other_expense['id']}", headers=owner).status_code == 404
    assert client.post(f"/api/v1/expenses/{other_expense['id']}/reverse", json={"reason": "Cross"}, headers=owner).status_code == 404
    assert client.post(f"/api/v1/expenses/{other_expense['id']}/archive", headers=owner).status_code == 404
    assert client.patch(f"/api/v1/expense-categories/{other_category['id']}", json={"name": "Cross"}, headers=owner).status_code == 404
    assert client.post(f"/api/v1/expense-categories/{other_category['id']}/archive", headers=owner).status_code == 404
    assert client.get("/api/v1/payments", headers=owner).json() == []
    assert client.get("/api/v1/expenses", headers=owner).json() == []
    assert client.get("/api/v1/expense-categories", headers=owner).json() == []


def test_invalid_cross_company_links_are_rejected(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    owner = owner_headers(client, seeded_identity)
    other = other_headers(client, seeded_identity)
    customer, _, project = create_project_fixture(client, owner)
    other_customer, _, other_project = create_project_fixture(client, other)
    other_estimate, _ = create_accepted_estimate(client, other, str(other_project["id"]))
    other_category = create_expense_category(client, other)
    other_supplier = create_supplier(client, other)
    other_material = create_material(client, other)

    payment_response = client.post(
        "/api/v1/payments",
        json={
            "customer_id": customer["id"],
            "project_id": project["id"],
            "estimate_id": other_estimate["id"],
            "amount": 100,
            "payment_method": "cash",
            "payment_date": "2026-07-08",
        },
        headers=owner,
    )
    assert payment_response.status_code == 404

    mismatched_customer_response = client.post(
        "/api/v1/payments",
        json={
            "customer_id": other_customer["id"],
            "project_id": project["id"],
            "amount": 100,
            "payment_method": "cash",
            "payment_date": "2026-07-08",
        },
        headers=owner,
    )
    assert mismatched_customer_response.status_code == 400

    for payload in [
        {"category_id": other_category["id"]},
        {"supplier_id": other_supplier["id"]},
        {"material_id": other_material["id"]},
    ]:
        expense_response = client.post(
            "/api/v1/expenses",
            json={
                "project_id": project["id"],
                "description": "Invalid link",
                "amount": 100,
                "expense_date": "2026-07-08",
                "payment_method": "cash",
                **payload,
            },
            headers=owner,
        )
        assert expense_response.status_code in {400, 404}


def test_payment_and_expense_endpoints_require_authentication(client: TestClient) -> None:
    endpoints: list[tuple[str, str, Optional[dict[str, object]]]] = [
        ("post", "/api/v1/payments", {"amount": 100}),
        ("get", "/api/v1/payments", None),
        ("get", "/api/v1/payments/missing", None),
        ("post", "/api/v1/payments/missing/reverse", {"reason": "No auth"}),
        ("post", "/api/v1/payments/missing/archive", None),
        ("get", "/api/v1/projects/missing/financial-summary", None),
        ("post", "/api/v1/expense-categories", {"name": "Materials"}),
        ("get", "/api/v1/expense-categories", None),
        ("patch", "/api/v1/expense-categories/missing", {"name": "Updated"}),
        ("post", "/api/v1/expense-categories/missing/archive", None),
        ("post", "/api/v1/expenses", {"amount": 100}),
        ("get", "/api/v1/expenses", None),
        ("get", "/api/v1/expenses/missing", None),
        ("post", "/api/v1/expenses/missing/reverse", {"reason": "No auth"}),
        ("post", "/api/v1/expenses/missing/archive", None),
    ]

    for method, path, payload in endpoints:
        response = getattr(client, method)(path, json=payload) if payload is not None else getattr(client, method)(path)
        assert response.status_code == 401
