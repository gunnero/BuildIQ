from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.estimate import EstimateItem
from app.services import estimate_documents as document_service
from tests.test_customers_properties import other_headers, owner_headers
from tests.test_estimates import create_estimate, create_estimate_item, first_revision
from tests.test_projects_tasks import create_project_fixture


@pytest.fixture()
def pdf_storage_path(tmp_path: Path) -> Path:
    settings = get_settings()
    original_storage_path = settings.storage_path
    settings.storage_path = str(tmp_path)
    try:
        yield tmp_path
    finally:
        settings.storage_path = original_storage_path


def create_pdf_ready_estimate(
    client: TestClient,
    headers: dict[str, str],
) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    _, _, project = create_project_fixture(client, headers)
    estimate = create_estimate(client, headers, str(project["id"]), title="Interior quote")
    revision = first_revision(client, headers, str(estimate["id"]))
    create_estimate_item(
        client,
        headers,
        str(revision["id"]),
        item_type="service",
        name="Wall finishing",
        quantity=2,
        unit_price=1500,
        unit="m2",
    )
    return project, estimate, revision


def test_generate_pdf_for_estimate_and_download_returns_pdf(
    client: TestClient,
    seeded_identity: dict[str, str],
    pdf_storage_path: Path,
) -> None:
    headers = owner_headers(client, seeded_identity)
    _, estimate, revision = create_pdf_ready_estimate(client, headers)

    response = client.post(
        f"/api/v1/estimates/{estimate['id']}/pdf",
        json={"revision_id": revision["id"]},
        headers=headers,
    )

    assert response.status_code == 201
    document = response.json()
    assert document["company_id"] == seeded_identity["demo_company_id"]
    assert document["estimate_id"] == estimate["id"]
    assert document["revision_id"] == revision["id"]
    assert document["document_type"] == "estimate_quote_pdf"
    assert document["generated_by_user_id"] == seeded_identity["owner_user_id"]
    assert document["archived_at"] is None
    assert document["file_path"].endswith(".pdf")
    assert (pdf_storage_path / document["file_path"]).exists()

    detail_response = client.get(
        f"/api/v1/estimate-documents/{document['id']}",
        headers=headers,
    )
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == document["id"]

    download_response = client.get(
        f"/api/v1/estimate-documents/{document['id']}/download",
        headers=headers,
    )
    assert download_response.status_code == 200
    assert download_response.headers["content-type"] == "application/pdf"
    assert download_response.content.startswith(b"%PDF")
    assert download_response.content.rstrip().endswith(b"%%EOF")
    assert len(download_response.content) > 1_000
    assert b"/Type /Page" in download_response.content


def test_generated_document_metadata_is_company_scoped(
    client: TestClient,
    seeded_identity: dict[str, str],
    pdf_storage_path: Path,
) -> None:
    owner = owner_headers(client, seeded_identity)
    other = other_headers(client, seeded_identity)
    _, estimate, revision = create_pdf_ready_estimate(client, other)

    response = client.post(
        f"/api/v1/estimates/{estimate['id']}/pdf",
        json={"revision_id": revision["id"]},
        headers=other,
    )
    assert response.status_code == 201
    document_id = response.json()["id"]

    assert client.get(f"/api/v1/estimate-documents/{document_id}", headers=owner).status_code == 404
    assert (
        client.get(
            f"/api/v1/estimate-documents/{document_id}/download",
            headers=owner,
        ).status_code
        == 404
    )


def test_archived_estimate_pdf_generation_is_rejected(
    client: TestClient,
    seeded_identity: dict[str, str],
    pdf_storage_path: Path,
) -> None:
    headers = owner_headers(client, seeded_identity)
    _, estimate, revision = create_pdf_ready_estimate(client, headers)
    archive_response = client.post(f"/api/v1/estimates/{estimate['id']}/archive", headers=headers)
    assert archive_response.status_code == 200

    response = client.post(
        f"/api/v1/estimates/{estimate['id']}/pdf",
        json={"revision_id": revision["id"]},
        headers=headers,
    )

    assert response.status_code == 400
    assert "архивирана" in response.json()["detail"]


def test_pdf_generation_uses_backend_revision_totals(
    client: TestClient,
    seeded_identity: dict[str, str],
    db_session: Session,
    pdf_storage_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    headers = owner_headers(client, seeded_identity)
    _, estimate, revision = create_pdf_ready_estimate(client, headers)
    item = db_session.query(EstimateItem).filter(EstimateItem.estimate_revision_id == revision["id"]).one()
    item.total_price = 4321.0
    db_session.add(item)
    db_session.commit()

    captured: dict[str, object] = {}

    def fake_write_estimate_pdf(**kwargs: object) -> None:
        output_path = Path(str(kwargs["output_path"]))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"%PDF-1.4\n%%EOF\n")
        captured["totals"] = kwargs["totals"]

    monkeypatch.setattr(document_service, "write_estimate_pdf", fake_write_estimate_pdf)

    response = client.post(
        f"/api/v1/estimates/{estimate['id']}/pdf",
        json={"revision_id": revision["id"]},
        headers=headers,
    )

    assert response.status_code == 201
    assert captured["totals"] == {
        "subtotal": 4321.0,
        "discount_total": 0.0,
        "adjustment_total": 0.0,
        "tax_total": 0.0,
        "total": 4321.0,
    }


def test_estimate_document_cross_company_generation_is_rejected(
    client: TestClient,
    seeded_identity: dict[str, str],
    pdf_storage_path: Path,
) -> None:
    owner = owner_headers(client, seeded_identity)
    other = other_headers(client, seeded_identity)
    _, estimate, revision = create_pdf_ready_estimate(client, other)

    response = client.post(
        f"/api/v1/estimates/{estimate['id']}/pdf",
        json={"revision_id": revision["id"]},
        headers=owner,
    )

    assert response.status_code == 404


def test_estimate_document_endpoints_require_authentication(client: TestClient) -> None:
    endpoints: list[tuple[str, str, dict[str, object] | None]] = [
        ("post", "/api/v1/estimates/missing/pdf", {"revision_id": "missing"}),
        ("get", "/api/v1/estimate-documents/missing", None),
        ("get", "/api/v1/estimate-documents/missing/download", None),
    ]

    for method, path, payload in endpoints:
        response = getattr(client, method)(path, json=payload) if payload is not None else getattr(client, method)(path)
        assert response.status_code == 401
