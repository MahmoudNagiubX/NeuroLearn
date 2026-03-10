from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.modules.events import repository
from app.modules.events.models import AppEvent
from app.modules.events.schemas import AppEventCreate


def log_event(
    db: Session,
    user_id: str | UUID,
    event_type: str,
    meta: dict[str, Any] | None = None,
) -> AppEvent:
    """
    Log a user event. Used directly by internal services.
    """
    return repository.create_event(db=db, user_id=user_id, event_type=event_type, meta=meta)


def create_event_from_api(
    db: Session,
    user_id: str | UUID,
    event_in: AppEventCreate,
) -> AppEvent:
    """
    Log a user event directly from the API.
    """
    return repository.create_event(
        db=db, 
        user_id=user_id, 
        event_type=event_in.event_type, 
        meta=event_in.meta
    )
