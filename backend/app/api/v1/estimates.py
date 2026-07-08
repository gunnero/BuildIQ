from typing import Optional

from fastapi import APIRouter, Depends, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_company, get_current_user
from app.core.config import Settings, get_settings
from app.core.errors import not_found
from app.db.session import get_db
from app.models.estimate import Estimate, EstimateDocument, EstimateItem, EstimateRevision
from app.models.identity import Company, User
from app.schemas.estimate import (
    EstimateCreate,
    EstimateDocumentResponse,
    EstimateFromCalculationCreate,
    EstimateItemCreate,
    EstimateItemResponse,
    EstimateItemUpdate,
    EstimatePdfCreate,
    EstimateResponse,
    EstimateRevisionResponse,
    EstimateStatusUpdate,
    EstimateUpdate,
)
from app.services.audit import record_audit_log
from app.services.estimate_documents import (
    create_estimate_pdf_document,
    get_estimate_document_for_company,
    resolve_storage_file_path,
)
from app.services.estimates import (
    archive_estimate,
    archive_estimate_item,
    calculate_revision_totals,
    change_estimate_status,
    create_estimate,
    create_estimate_from_calculation,
    create_estimate_item,
    get_active_estimate_for_company,
    get_estimate_for_company,
    get_item_for_company,
    get_revision_for_company,
    ensure_estimate_editable,
    update_estimate_item,
)

router = APIRouter(tags=["estimates"])


def estimate_response(estimate: Estimate) -> EstimateResponse:
    return EstimateResponse(
        id=estimate.id,
        company_id=estimate.company_id,
        customer_id=estimate.customer_id,
        property_id=estimate.property_id,
        project_id=estimate.project_id,
        estimate_number=estimate.estimate_number,
        title=estimate.title,
        description=estimate.description,
        status=estimate.status,
        source_calculation_run_id=estimate.source_calculation_run_id,
        sent_at=estimate.sent_at,
        accepted_at=estimate.accepted_at,
        rejected_at=estimate.rejected_at,
        archived_at=estimate.archived_at,
        created_at=estimate.created_at,
        updated_at=estimate.updated_at,
    )


def revision_response(revision: EstimateRevision) -> EstimateRevisionResponse:
    totals = calculate_revision_totals(revision)
    return EstimateRevisionResponse(
        id=revision.id,
        company_id=revision.company_id,
        estimate_id=revision.estimate_id,
        revision_number=revision.revision_number,
        status=revision.status,
        notes=revision.notes,
        terms=revision.terms,
        source_calculation_run_id=revision.source_calculation_run_id,
        sent_at=revision.sent_at,
        accepted_at=revision.accepted_at,
        rejected_at=revision.rejected_at,
        archived_at=revision.archived_at,
        created_at=revision.created_at,
        updated_at=revision.updated_at,
        **totals,
    )


def item_response(item: EstimateItem) -> EstimateItemResponse:
    return EstimateItemResponse(
        id=item.id,
        company_id=item.company_id,
        estimate_revision_id=item.estimate_revision_id,
        item_type=item.item_type,
        name=item.name,
        description=item.description,
        material_id=item.material_id,
        quantity=item.quantity,
        unit=item.unit,
        unit_price=item.unit_price,
        total_price=item.total_price,
        source_calculation_run_id=item.source_calculation_run_id,
        source_calculation_line_item_id=item.source_calculation_line_item_id,
        sort_order=item.sort_order,
        archived_at=item.archived_at,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def estimate_document_response(document: EstimateDocument) -> EstimateDocumentResponse:
    return EstimateDocumentResponse(
        id=document.id,
        company_id=document.company_id,
        estimate_id=document.estimate_id,
        revision_id=document.revision_id,
        document_type=document.document_type,
        file_path=document.file_path,
        generated_by_user_id=document.generated_by_user_id,
        generated_at=document.generated_at,
        archived_at=document.archived_at,
        created_at=document.created_at,
        updated_at=document.updated_at,
    )


@router.post("/estimates", response_model=EstimateResponse, status_code=status.HTTP_201_CREATED)
def create_estimate_endpoint(
    payload: EstimateCreate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> EstimateResponse:
    estimate = create_estimate(db, company_id=company.id, payload=payload)
    db.commit()
    db.refresh(estimate)
    return estimate_response(estimate)


@router.post(
    "/estimates/{estimate_id}/pdf",
    response_model=EstimateDocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_estimate_pdf(
    estimate_id: str,
    payload: Optional[EstimatePdfCreate] = None,
    company: Company = Depends(get_current_company),
    current_user: User = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
) -> EstimateDocumentResponse:
    estimate = get_estimate_for_company(db, company_id=company.id, estimate_id=estimate_id)
    document = create_estimate_pdf_document(
        db,
        company=company,
        current_user=current_user,
        estimate=estimate,
        revision_id=payload.revision_id if payload is not None else None,
        storage_path=settings.storage_path,
    )
    db.commit()
    db.refresh(document)
    return estimate_document_response(document)


@router.get("/estimate-documents/{document_id}", response_model=EstimateDocumentResponse)
def read_estimate_document(
    document_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> EstimateDocumentResponse:
    document = get_estimate_document_for_company(
        db,
        company_id=company.id,
        document_id=document_id,
    )
    return estimate_document_response(document)


@router.get(
    "/estimate-documents/{document_id}/download",
    response_class=FileResponse,
    responses={200: {"content": {"application/pdf": {}}}},
)
def download_estimate_document(
    document_id: str,
    company: Company = Depends(get_current_company),
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
) -> FileResponse:
    document = get_estimate_document_for_company(
        db,
        company_id=company.id,
        document_id=document_id,
    )
    file_path = resolve_storage_file_path(settings.storage_path, document.file_path)
    if not file_path.exists():
        raise not_found("PDF документот не е пронајден.")
    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename=f"ponuda-{document.estimate_id}-{document.revision_id}.pdf",
    )


@router.get("/estimates", response_model=list[EstimateResponse])
def list_estimates(
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> list[EstimateResponse]:
    estimates = (
        db.query(Estimate)
        .filter(
            Estimate.company_id == company.id,
            Estimate.archived_at.is_(None),
        )
        .order_by(Estimate.created_at.asc())
        .all()
    )
    return [estimate_response(estimate) for estimate in estimates]


@router.get("/estimates/{estimate_id}", response_model=EstimateResponse)
def read_estimate(
    estimate_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> EstimateResponse:
    estimate = get_active_estimate_for_company(db, company_id=company.id, estimate_id=estimate_id)
    return estimate_response(estimate)


@router.patch("/estimates/{estimate_id}", response_model=EstimateResponse)
def update_estimate(
    estimate_id: str,
    payload: EstimateUpdate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> EstimateResponse:
    estimate = get_active_estimate_for_company(db, company_id=company.id, estimate_id=estimate_id)
    ensure_estimate_editable(estimate)
    if payload.title is not None:
        estimate.title = payload.title
    if payload.description is not None:
        estimate.description = payload.description
    db.add(estimate)
    db.commit()
    db.refresh(estimate)
    return estimate_response(estimate)


@router.post("/estimates/{estimate_id}/archive", response_model=EstimateResponse)
def archive_estimate_endpoint(
    estimate_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> EstimateResponse:
    estimate = get_active_estimate_for_company(db, company_id=company.id, estimate_id=estimate_id)
    archive_estimate(estimate)
    db.add(estimate)
    db.commit()
    db.refresh(estimate)
    return estimate_response(estimate)


@router.post("/estimates/{estimate_id}/status", response_model=EstimateResponse)
def change_estimate_status_endpoint(
    estimate_id: str,
    payload: EstimateStatusUpdate,
    company: Company = Depends(get_current_company),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> EstimateResponse:
    estimate = get_active_estimate_for_company(db, company_id=company.id, estimate_id=estimate_id)
    before_status = estimate.status
    change_estimate_status(estimate, status_value=payload.status)
    record_audit_log(
        db,
        action="estimate.status_changed",
        entity_type="estimate",
        entity_id=estimate.id,
        company_id=company.id,
        acting_user_id=current_user.id,
        before_snapshot={"status": before_status},
        after_snapshot={"status": estimate.status},
    )
    db.add(estimate)
    db.commit()
    db.refresh(estimate)
    return estimate_response(estimate)


@router.post(
    "/estimates/from-calculation/{calculation_run_id}",
    response_model=EstimateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_estimate_from_calculation_endpoint(
    calculation_run_id: str,
    payload: EstimateFromCalculationCreate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> EstimateResponse:
    estimate = create_estimate_from_calculation(
        db,
        company_id=company.id,
        calculation_run_id=calculation_run_id,
        payload=payload,
    )
    db.commit()
    db.refresh(estimate)
    return estimate_response(estimate)


@router.get("/estimates/{estimate_id}/revisions", response_model=list[EstimateRevisionResponse])
def list_estimate_revisions(
    estimate_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> list[EstimateRevisionResponse]:
    estimate = get_active_estimate_for_company(db, company_id=company.id, estimate_id=estimate_id)
    revisions = [
        revision
        for revision in sorted(estimate.revisions, key=lambda item: item.revision_number)
        if revision.archived_at is None
    ]
    return [revision_response(revision) for revision in revisions]


@router.get("/estimate-revisions/{revision_id}", response_model=EstimateRevisionResponse)
def read_estimate_revision(
    revision_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> EstimateRevisionResponse:
    revision = get_revision_for_company(db, company_id=company.id, revision_id=revision_id)
    return revision_response(revision)


@router.post(
    "/estimate-revisions/{revision_id}/items",
    response_model=EstimateItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_estimate_item_endpoint(
    revision_id: str,
    payload: EstimateItemCreate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> EstimateItemResponse:
    revision = get_revision_for_company(db, company_id=company.id, revision_id=revision_id)
    item = create_estimate_item(db, company_id=company.id, revision=revision, payload=payload)
    db.commit()
    db.refresh(item)
    return item_response(item)


@router.get("/estimate-revisions/{revision_id}/items", response_model=list[EstimateItemResponse])
def list_estimate_items(
    revision_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> list[EstimateItemResponse]:
    revision = get_revision_for_company(db, company_id=company.id, revision_id=revision_id)
    items = [
        item
        for item in sorted(revision.items, key=lambda item: item.sort_order)
        if item.archived_at is None
    ]
    return [item_response(item) for item in items]


@router.patch("/estimate-items/{item_id}", response_model=EstimateItemResponse)
def update_estimate_item_endpoint(
    item_id: str,
    payload: EstimateItemUpdate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> EstimateItemResponse:
    item = get_item_for_company(db, company_id=company.id, item_id=item_id)
    update_estimate_item(db, company_id=company.id, item=item, payload=payload)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item_response(item)


@router.post("/estimate-items/{item_id}/archive", response_model=EstimateItemResponse)
def archive_estimate_item_endpoint(
    item_id: str,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> EstimateItemResponse:
    item = get_item_for_company(db, company_id=company.id, item_id=item_id)
    archive_estimate_item(item)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item_response(item)
