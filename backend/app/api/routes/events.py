import uuid
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps.auth_dependencies import get_current_user
from app.core.database.session import get_db
from app.modules.events import schemas, service

router = APIRouter()

@router.post("", response_model=schemas.AppEventResponse)
def log_event(
    event_in: schemas.AppEventCreate,
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user),
) -> Any:
    """
    Log an event.
    """
    return service.create_event_from_api(
        db=db,
        user_id=current_user_id,
        event_in=event_in
    )
