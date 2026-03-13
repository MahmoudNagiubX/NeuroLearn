from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps.auth_dependencies import get_current_user_id
from app.core.database.session import get_db
from app.modules.events import schemas

router = APIRouter()


@router.get("", response_model=list[schemas.EventResponse])
def list_events(
    db: Annotated[Session, Depends(get_db)],
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> Any:
    """
    List recent events for the current user.
    """
    from app.modules.events.repository import repository
    events = repository.get_user_events(db, user_id=current_user_id, limit=50)
    return events
