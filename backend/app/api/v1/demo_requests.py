from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.models.demo_request import DemoRequest
from app.models.identity import User
from app.schemas.demo_request import DemoActivation, DemoRequestCreate, DemoRequestView
from app.services import demo_requests

router = APIRouter(prefix="/demo-requests", tags=["demo requests"])


def enabled_settings(settings: Settings = Depends(get_settings)) -> Settings:
    if not settings.demo_requests_enabled:
        raise HTTPException(503, "Демо барањата моментално не се достапни.")
    return settings


def reviewer(user: User = Depends(get_current_user)) -> User:
    if not user.is_hq_admin:
        raise HTTPException(403, "Немате дозвола за оваа акција.")
    return user


@router.get("/availability")
def availability(settings: Settings = Depends(get_settings)) -> dict[str, bool]:
    return {"enabled": settings.demo_requests_enabled}


@router.post("", status_code=202, response_class=Response)
def submit_request(
    payload: DemoRequestCreate,
    request: Request,
    settings: Settings = Depends(enabled_settings),
    db: Session = Depends(get_db),
) -> Response:
    demo_requests.submit(db, settings, payload, request.client.host if request.client else "unknown")
    return Response(status_code=202)


@router.post("/activate")
def activate_request(
    payload: DemoActivation,
    settings: Settings = Depends(enabled_settings),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    return {"email": demo_requests.activate(db, settings, payload)}


@router.get("", response_model=list[DemoRequestView], dependencies=[Depends(reviewer)])
def list_requests(
    state: Literal["pending", "approved"] = "pending",
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[DemoRequest]:
    condition = DemoRequest.approved_at.is_(None) if state == "pending" else DemoRequest.approved_at.is_not(None)
    return list(db.scalars(select(DemoRequest).where(condition)
                           .order_by(DemoRequest.created_at.desc(), DemoRequest.id)
                           .offset(offset).limit(limit)))


@router.get("/{request_id}", response_model=DemoRequestView, dependencies=[Depends(reviewer)])
def get_request(request_id: str, db: Session = Depends(get_db)) -> DemoRequest:
    item = db.get(DemoRequest, request_id)
    if item is None:
        raise HTTPException(404, "Барањето не е пронајдено.")
    return item


@router.post("/{request_id}/approve", response_model=DemoRequestView,
             dependencies=[Depends(enabled_settings)])
def approve_request(
    request_id: str, user: User = Depends(reviewer), db: Session = Depends(get_db),
) -> DemoRequest:
    return demo_requests.approve(db, request_id, user)
