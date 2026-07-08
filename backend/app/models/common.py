from datetime import datetime
import uuid

from sqlalchemy import Column, DateTime, String


def generate_uuid() -> str:
    return str(uuid.uuid4())


class IdMixin:
    id = Column(String(36), primary_key=True, default=generate_uuid)


class TimestampMixin:
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
