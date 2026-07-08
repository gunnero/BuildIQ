from typing import Any, Optional

from sqlalchemy.orm import Session

from app.models.kernel import AuditLog


def record_audit_log(
    db: Session,
    *,
    action: str,
    entity_type: str,
    entity_id: Optional[str] = None,
    company_id: Optional[str] = None,
    acting_user_id: Optional[str] = None,
    before_snapshot: Optional[dict[str, Any]] = None,
    after_snapshot: Optional[dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> AuditLog:
    log = AuditLog(
        company_id=company_id,
        acting_user_id=acting_user_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        before_snapshot=before_snapshot,
        after_snapshot=after_snapshot,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(log)
    return log
