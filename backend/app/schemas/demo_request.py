from datetime import datetime
import re
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

ShortText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]


class DemoRequestCreate(BaseModel):
    name: ShortText
    email: Annotated[str, StringConstraints(strip_whitespace=True, max_length=254)]
    company_name: ShortText
    message: Annotated[str, StringConstraints(strip_whitespace=True, max_length=1000)] = ""

    @field_validator("email")
    @classmethod
    def valid_email(cls, value: str) -> str:
        local, _, domain = value.rpartition("@")
        atom = r"[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+"
        label = r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
        if (len(local) > 64 or not re.fullmatch(rf"{atom}(?:\.{atom})*", local)
                or not re.fullmatch(rf"{label}(?:\.{label})+", domain)):
            raise ValueError("Invalid email address")
        return value.lower()


class DemoActivation(BaseModel):
    token: str = Field(pattern=r"^[a-f0-9-]{36}\.[a-f0-9]{64}$")
    password: str = Field(min_length=12, max_length=128)


class DemoRequestView(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: str
    company_name: str
    message: str
    created_at: datetime
    approved_at: datetime | None
    activated_at: datetime | None
    invitation_sent_at: datetime | None
