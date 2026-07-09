from fastapi.testclient import TestClient

from tests.test_calculations import run_calculation
from tests.test_customers_properties import create_customer, other_headers, owner_headers
from tests.test_estimates import create_estimate
from tests.test_materials import create_material
from tests.test_payments_expenses import create_expense, create_expense_category, create_payment
from tests.test_procurement import create_supplier
from tests.test_projects_tasks import create_project_fixture


def response_ids(client: TestClient, path: str, headers: dict[str, str]) -> set[str]:
    response = client.get(path, headers=headers)
    assert response.status_code == 200
    return {item["id"] for item in response.json()}


def assert_company_scoped_list(
    client: TestClient,
    path: str,
    owner_headers_value: dict[str, str],
    other_headers_value: dict[str, str],
    owner_id: str,
    other_id: str,
) -> None:
    owner_ids = response_ids(client, path, owner_headers_value)
    other_ids = response_ids(client, path, other_headers_value)

    assert owner_id in owner_ids
    assert other_id not in owner_ids
    assert other_id in other_ids
    assert owner_id not in other_ids


def test_core_business_list_endpoints_are_company_scoped(
    client: TestClient,
    seeded_identity: dict[str, str],
) -> None:
    owner = owner_headers(client, seeded_identity)
    other = other_headers(client, seeded_identity)

    owner_customer, _, owner_project = create_project_fixture(client, owner)
    other_customer, _, other_project = create_project_fixture(client, other)

    owner_extra_customer = create_customer(client, owner, name="Aleksandar-only customer")
    other_extra_customer = create_customer(client, other, name="Hristijan-only customer")

    owner_material = create_material(client, owner, name="Aleksandar-only paint")
    other_material = create_material(client, other, name="Hristijan-only paint")

    owner_supplier = create_supplier(client, owner, name="Aleksandar-only supplier")
    other_supplier = create_supplier(client, other, name="Hristijan-only supplier")

    owner_calculation = run_calculation(
        client,
        owner,
        engine_type="tiles",
        project_id=str(owner_project["id"]),
    )
    other_calculation = run_calculation(
        client,
        other,
        engine_type="tiles",
        project_id=str(other_project["id"]),
    )

    owner_estimate = create_estimate(client, owner, str(owner_project["id"]), title="Aleksandar offer")
    other_estimate = create_estimate(client, other, str(other_project["id"]), title="Hristijan offer")

    owner_payment = create_payment(
        client,
        owner,
        str(owner_customer["id"]),
        str(owner_project["id"]),
        estimate_id=str(owner_estimate["id"]),
        note="Aleksandar payment",
    )
    other_payment = create_payment(
        client,
        other,
        str(other_customer["id"]),
        str(other_project["id"]),
        estimate_id=str(other_estimate["id"]),
        note="Hristijan payment",
    )

    owner_expense_category = create_expense_category(client, owner, name="Aleksandar materials")
    other_expense_category = create_expense_category(client, other, name="Hristijan materials")
    owner_expense = create_expense(
        client,
        owner,
        project_id=str(owner_project["id"]),
        category_id=str(owner_expense_category["id"]),
        supplier_id=str(owner_supplier["id"]),
        material_id=str(owner_material["id"]),
    )
    other_expense = create_expense(
        client,
        other,
        project_id=str(other_project["id"]),
        category_id=str(other_expense_category["id"]),
        supplier_id=str(other_supplier["id"]),
        material_id=str(other_material["id"]),
    )

    assert_company_scoped_list(
        client,
        "/api/v1/customers",
        owner,
        other,
        str(owner_extra_customer["id"]),
        str(other_extra_customer["id"]),
    )
    assert_company_scoped_list(
        client,
        "/api/v1/projects",
        owner,
        other,
        str(owner_project["id"]),
        str(other_project["id"]),
    )
    assert_company_scoped_list(
        client,
        "/api/v1/materials",
        owner,
        other,
        str(owner_material["id"]),
        str(other_material["id"]),
    )
    assert_company_scoped_list(
        client,
        "/api/v1/suppliers",
        owner,
        other,
        str(owner_supplier["id"]),
        str(other_supplier["id"]),
    )
    assert_company_scoped_list(
        client,
        "/api/v1/calculations",
        owner,
        other,
        str(owner_calculation["id"]),
        str(other_calculation["id"]),
    )
    assert_company_scoped_list(
        client,
        "/api/v1/estimates",
        owner,
        other,
        str(owner_estimate["id"]),
        str(other_estimate["id"]),
    )
    assert_company_scoped_list(
        client,
        "/api/v1/payments",
        owner,
        other,
        str(owner_payment["id"]),
        str(other_payment["id"]),
    )
    assert_company_scoped_list(
        client,
        "/api/v1/expenses",
        owner,
        other,
        str(owner_expense["id"]),
        str(other_expense["id"]),
    )
