from datetime import datetime, timedelta, timezone
from hashlib import sha256
import hmac

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.security import hash_password
from app.models.demo_request import DemoRequest
from app.models.identity import Company, Role, User, UserRole
from app.models.subscription import Subscription, SubscriptionPlan
from app.schemas.demo_request import DemoActivation, DemoRequestCreate
from app.services.audit import record_audit_log
from app.services.auth import get_user_by_email

INVITE_LIFETIME = timedelta(days=7)
TRIAL_LIFETIME = timedelta(days=14)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value


def signature(settings: Settings, purpose: str, value: str) -> str:
    return hmac.new(settings.jwt_secret_key.encode(), f"{purpose}:{value}".encode(), sha256).hexdigest()


def invitation_token(settings: Settings, item: DemoRequest) -> str:
    return f"{item.id}.{signature(settings, 'demo-invitation-v1', item.id)}"


def submit(db: Session, settings: Settings, payload: DemoRequestCreate, client_ip: str) -> None:
    # Use the same response for duplicates and emails already registered with BuildIQ.
    if get_user_by_email(db, payload.email) or db.scalar(
        select(DemoRequest.id).where(DemoRequest.email == payload.email)
    ):
        return
    now = utc_now()
    source_key = signature(settings, "demo-request-source", client_ip)
    recent = DemoRequest.created_at >= now - timedelta(hours=1)
    count = select(func.count()).select_from(DemoRequest).where(recent)
    if db.scalar(count.where(DemoRequest.source_key == source_key)) >= 4 or db.scalar(count) >= 40:
        raise HTTPException(429, "Премногу барања. Обидете се повторно подоцна.")
    db.add(DemoRequest(**payload.model_dump(), source_key=source_key, next_email_at=now))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        if not db.scalar(select(DemoRequest.id).where(DemoRequest.email == payload.email)):
            raise


def approve(db: Session, request_id: str, reviewer: User) -> DemoRequest:
    item = db.scalar(select(DemoRequest).where(DemoRequest.id == request_id).with_for_update())
    if item is None:
        raise HTTPException(404, "Барањето не е пронајдено.")
    if item.approved_at is None:
        if get_user_by_email(db, item.email):
            raise HTTPException(409, "Веќе постои корисник со оваа е-пошта.")
        now = utc_now()
        item.approved_at = now
        item.approved_by = reviewer.id
        item.email_attempts = 0
        item.next_email_at = now
        record_audit_log(db, action="demo_request.approved", entity_type="demo_request",
                         entity_id=item.id, acting_user_id=reviewer.id, company_id=reviewer.company_id)
        db.commit()
        db.refresh(item)
    return item


def activate(db: Session, settings: Settings, payload: DemoActivation) -> str:
    request_id, _, proof = payload.token.partition(".")
    expected = signature(settings, "demo-invitation-v1", request_id)
    invalid = HTTPException(400, "Врската е неважечка, истечена или веќе искористена.")
    if not proof.isascii() or not hmac.compare_digest(proof, expected):
        raise invalid
    item = db.scalar(select(DemoRequest).where(DemoRequest.id == request_id).with_for_update())
    now = utc_now()
    if (item is None or item.approved_at is None or item.activated_at is not None
            or as_utc(item.approved_at) + INVITE_LIFETIME <= now
            or get_user_by_email(db, item.email)):
        raise invalid
    plan = db.scalar(select(SubscriptionPlan).where(
        SubscriptionPlan.key == "demo-trial", SubscriptionPlan.is_active.is_(True),
    ))
    if plan is None:
        raise HTTPException(503, "Демо пристапот моментално не е достапен.")

    expires = now + TRIAL_LIFETIME
    company = Company(name=f"{item.company_name} · Демо")
    db.add(company)
    db.flush()
    owner = User(company_id=company.id, name=item.name, email=item.email,
                 password_hash=hash_password(payload.password), access_expires_at=expires)
    role = Role(company_id=company.id, key="owner", name="Owner", is_system_role=True)
    db.add_all([owner, role])
    try:
        db.flush()
        db.add_all([
            UserRole(user_id=owner.id, role_id=role.id),
            Subscription(company_id=company.id, plan_id=plan.id, status="trialing",
                         starts_on=now.date(), trial_ends_on=expires.date()),
        ])
        item.user_id = owner.id
        item.activated_at = now
        item.next_email_at = None
        db.commit()
    except IntegrityError:
        db.rollback()
        if get_user_by_email(db, item.email):
            raise invalid from None
        raise
    return owner.email
