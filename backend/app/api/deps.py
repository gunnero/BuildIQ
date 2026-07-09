from datetime import date
from typing import Any, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.identity import Company, User
from app.models.subscription import Subscription

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def authentication_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не сте најавени.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    if token is None:
        raise authentication_error()

    try:
        payload: dict[str, Any] = decode_access_token(token)
    except jwt.PyJWTError as exc:
        raise authentication_error() from exc

    user_id = payload.get("sub")
    company_id = payload.get("company_id")
    if not user_id or not company_id:
        raise authentication_error()

    user = db.query(User).filter(User.id == user_id, User.status == "active").one_or_none()
    if user is None or user.company_id != company_id:
        raise authentication_error()

    return user


def get_current_company(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Company:
    company = (
        db.query(Company)
        .filter(Company.id == current_user.company_id, Company.status == "active")
        .one_or_none()
    )
    if company is None:
        raise authentication_error()

    path = request.url.path
    if not (path.endswith("/companies/me") or path.endswith("/subscription/me")):
        subscription = (
            db.query(Subscription)
            .filter(Subscription.company_id == company.id)
            .order_by(Subscription.created_at.desc())
            .first()
        )
        today = date.today()
        subscription_active = bool(
            subscription is not None
            and subscription.status in {"active", "trialing"}
            and (subscription.starts_on is None or subscription.starts_on <= today)
            and (subscription.ends_on is None or subscription.ends_on >= today)
            and (subscription.trial_ends_on is None or subscription.trial_ends_on >= today)
        )
        if not subscription_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Компанијата нема активна претплата.",
            )

        permission_key = _route_permission_key(request)
        if permission_key is not None:
            from app.services.authorization import user_has_permission

            db.expire(current_user, ["user_roles"])
            db.refresh(current_user)
            if not user_has_permission(current_user, permission_key, db):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Немате дозвола за оваа акција.",
                )
    return company


def _route_permission_key(request: Request) -> Optional[str]:
    path = request.url.path.lower()
    domain = next(
        (
            name
            for marker, name in (
                ("/customers", "customers"),
                ("/properties", "properties"),
                ("/tasks", "tasks"),
                ("/rooms", "rooms"),
                ("/measurement", "measurements"),
                ("/calculations", "calculations"),
                ("/calculation-", "calculations"),
                ("/material-", "materials"),
                ("/material-price", "procurement"),
                ("/financial-summary", "financial"),
                ("/projects", "projects"),
                ("/materials", "materials"),
                ("/suppliers", "procurement"),
                ("/price-books", "procurement"),
                ("/price-book-items", "procurement"),
                ("/supplier-", "procurement"),
                ("/estimates", "estimates"),
                ("/estimate-", "estimates"),
                ("/payments", "financial"),
                ("/expenses", "financial"),
            )
            if marker in path
        ),
        None,
    )
    if domain is None:
        return None
    if request.method == "GET":
        return f"{domain}:read"
    if domain == "measurements" and request.method == "POST":
        return "measurements:create"
    if domain == "calculations" and request.method == "POST":
        return "calculations:create"
    return f"{domain}:write"
