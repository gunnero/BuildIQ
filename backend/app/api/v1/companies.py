from fastapi import APIRouter, Depends

from app.api.deps import get_current_company
from app.models.identity import Company
from app.schemas.company import CompanyResponse

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("/me", response_model=CompanyResponse)
def read_current_company(company: Company = Depends(get_current_company)) -> CompanyResponse:
    return CompanyResponse(
        id=company.id,
        name=company.name,
        tax_number=company.tax_number,
        address=company.address,
        phone=company.phone,
        email=company.email,
        status=company.status,
        is_internal=company.is_internal,
        created_at=company.created_at,
        updated_at=company.updated_at,
    )
