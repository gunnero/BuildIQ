from typing import Any, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.identity import Company, User

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
    return company
