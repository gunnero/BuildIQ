from collections.abc import Callable
from typing import Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.identity import Permission, Role, RolePermission, User, UserRole


PERMISSION_KEYS = (
    "customers",
    "properties",
    "projects",
    "tasks",
    "rooms",
    "measurements",
    "materials",
    "procurement",
    "calculations",
    "estimates",
    "financial",
)


RC1_ROLE_PERMISSIONS: dict[str, set[str]] = {
    "owner": {f"{domain}:{action}" for domain in PERMISSION_KEYS for action in ("read", "write")},
    "manager": {f"{domain}:{action}" for domain in PERMISSION_KEYS for action in ("read", "write")},
    "worker": {
        "projects:read",
        "tasks:read",
        "rooms:read",
        "measurements:read",
        "measurements:create",
        "calculations:read",
        "calculations:create",
    },
    "accountant": {
        "financial:read",
        "financial:write",
        "estimates:read",
        "estimates:write",
    },
}


def get_user_permission_keys(user: User) -> set[str]:
    permission_keys: set[str] = set()
    for user_role in user.user_roles:
        role_key = user_role.role.key
        if role_key in RC1_ROLE_PERMISSIONS:
            permission_keys.update(RC1_ROLE_PERMISSIONS[role_key])
        for role_permission in user_role.role.role_permissions:
            permission_keys.add(role_permission.permission.key)
    return permission_keys


def user_has_permission(user: User, permission_key: str, db: Optional[Session] = None) -> bool:
    if db is not None:
        role_keys = {
            role_key
            for (role_key,) in db.query(Role.key)
            .join(UserRole, UserRole.role_id == Role.id)
            .filter(UserRole.user_id == user.id)
            .all()
        }
        if "owner" in role_keys:
            return True
        if any(
            permission_key in RC1_ROLE_PERMISSIONS.get(role_key, set())
            for role_key in role_keys
        ):
            return True
        permission_exists = (
            db.query(Permission.id)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(Role, Role.id == RolePermission.role_id)
            .join(UserRole, UserRole.role_id == Role.id)
            .filter(UserRole.user_id == user.id, Permission.key == permission_key)
            .first()
        )
        if permission_exists is not None:
            return True
    return permission_key in get_user_permission_keys(user)


def require_permission(permission_key: str) -> Callable[..., User]:
    def dependency(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ) -> User:
        db.refresh(current_user)
        if not user_has_permission(current_user, permission_key, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Немате дозвола за оваа акција.",
            )
        return current_user

    return dependency
