from pydantic import BaseModel


class SubscriptionPlanResponse(BaseModel):
    id: str
    key: str
    name: str
    price_mkd: int
    billing_period: str
    is_active: bool


class SubscriptionResponse(BaseModel):
    id: str
    company_id: str
    status: str
    plan: SubscriptionPlanResponse
