from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_company
from app.db.session import get_db
from app.models.identity import Company
from app.models.subscription import Subscription
from app.schemas.subscription import SubscriptionPlanResponse, SubscriptionResponse

router = APIRouter(prefix="/subscription", tags=["subscriptions"])


@router.get("/me", response_model=SubscriptionResponse)
def read_current_subscription(
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> SubscriptionResponse:
    subscription = (
        db.query(Subscription)
        .filter(Subscription.company_id == company.id)
        .order_by(Subscription.created_at.desc())
        .first()
    )
    if subscription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Нема активна претплата.",
        )

    return SubscriptionResponse(
        id=subscription.id,
        company_id=subscription.company_id,
        status=subscription.status,
        created_at=subscription.created_at,
        updated_at=subscription.updated_at,
        plan=SubscriptionPlanResponse(
            id=subscription.plan.id,
            key=subscription.plan.key,
            name=subscription.plan.name,
            price_mkd=subscription.plan.price_mkd,
            billing_period=subscription.plan.billing_period,
            is_active=subscription.plan.is_active,
            created_at=subscription.plan.created_at,
            updated_at=subscription.plan.updated_at,
        ),
    )
