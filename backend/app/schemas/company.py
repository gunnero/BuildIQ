from typing import Optional

from pydantic import BaseModel


class CompanyResponse(BaseModel):
    id: str
    name: str
    tax_number: Optional[str]
    address: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    status: str
    is_internal: bool
