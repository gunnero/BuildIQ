from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CurrentUserResponse(BaseModel):
    id: str
    company_id: str
    name: str
    email: str
    status: str
    is_hq_admin: bool
    roles: list[str]
