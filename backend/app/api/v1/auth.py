from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import create_access_token
from app.db.session import get_db
from app.models.identity import User
from app.schemas.auth import CurrentUserResponse, LoginRequest, TokenResponse
from app.services.audit import record_audit_log
from app.services.auth import authenticate_user

router = APIRouter(prefix="/auth", tags=["auth"])


def build_current_user_response(user: User) -> CurrentUserResponse:
    return CurrentUserResponse(
        id=user.id,
        company_id=user.company_id,
        name=user.name,
        email=user.email,
        status=user.status,
        is_hq_admin=user.is_hq_admin,
        roles=[user_role.role.key for user_role in user.user_roles],
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.post("/login", response_model=TokenResponse, summary="Log in")
def login(
    payload: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> TokenResponse:
    user = authenticate_user(db, payload.email, payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидни податоци за најава.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    record_audit_log(
        db,
        action="auth.login_success",
        entity_type="user",
        entity_id=user.id,
        company_id=user.company_id,
        acting_user_id=user.id,
        after_snapshot={"email": user.email},
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    db.commit()
    return TokenResponse(access_token=create_access_token(user.id, user.company_id))


@router.get("/me", response_model=CurrentUserResponse, summary="Read current user")
def read_current_user(current_user: User = Depends(get_current_user)) -> CurrentUserResponse:
    return build_current_user_response(current_user)
