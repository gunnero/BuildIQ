from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.models.identity import User


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return (
        db.query(User)
        .filter(func.lower(User.email) == email.strip().lower())
        .one_or_none()
    )


def user_access_active(user: User) -> bool:
    expires = user.access_expires_at
    if expires is not None and expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    return user.status == "active" and (expires is None or expires > datetime.now(timezone.utc))


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if user is None:
        return None
    if not user_access_active(user):
        return None
    if not verify_password(password, user.password_hash):
        return None

    user.last_login_at = datetime.utcnow()
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
