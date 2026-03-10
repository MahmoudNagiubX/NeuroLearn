from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.modules.events.models import AppEvent


def create_event(
    db: Session,
    user_id: str |  UUID,
    event_type: str,
    meta: dict[str, Any] | None = None,
) -> AppEvent:
    db_event = AppEvent(
        user_id=user_id,
        event_type=event_type,
        meta=meta
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event
