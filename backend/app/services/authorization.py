from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.identity import User


def get_user_permission_keys(user: User) -> set[str]:
    permission_keys: set[str] = set()
    for user_role in user.user_roles:
        for role_permission in user_role.role.role_permissions:
            permission_keys.add(role_permission.permission.key)
    return permission_keys


def user_has_permission(user: User, permission_key: str) -> bool:
    return permission_key in get_user_permission_keys(user)


def require_permission(permission_key: str) -> Callable[..., User]:
    def dependency(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ) -> User:
        db.refresh(current_user)
        if not user_has_permission(current_user, permission_key):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Немате дозвола за оваа акција.",
            )
        return current_user

    return dependency
