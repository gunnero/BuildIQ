from datetime import datetime
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


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if user is None:
        return None
    if user.status != "active":
        return None
    if not verify_password(password, user.password_hash):
        return None

    user.last_login_at = datetime.utcnow()
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
