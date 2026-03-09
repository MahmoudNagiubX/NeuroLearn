from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps.auth_dependencies import get_current_user
from app.core.database.session import get_db
from app.modules.pomodoro.models import PomodoroStatus
from app.modules.pomodoro.schemas import (
    PomodoroCompleteRequest,
    PomodoroSessionCreate,
    PomodoroSessionRead,
    PomodoroSessionUpdate,
)
from app.modules.pomodoro.service import (
    CrossEntityValidationError,
    PomodoroStateError,
    complete_pomodoro_session,
    create_pomodoro_session,
    get_pomodoro_session,
    list_pomodoro_sessions,
    update_pomodoro_session,
)
from app.modules.users.models import User


router = APIRouter(prefix="/pomodoro-sessions", tags=["pomodoro-sessions"])


@router.post("", response_model=PomodoroSessionRead, status_code=status.HTTP_201_CREATED)
def create_pomodoro_session_endpoint(
    payload: PomodoroSessionCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> PomodoroSessionRead:
    try:
        pomodoro_session = create_pomodoro_session(db, user_id=current_user.id, payload=payload)
    except (CrossEntityValidationError, PomodoroStateError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return PomodoroSessionRead.model_validate(pomodoro_session)


@router.get("", response_model=list[PomodoroSessionRead])
def list_pomodoro_sessions_endpoint(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    subject_id: UUID | None = None,
    task_id: UUID | None = None,
    status_filter: Annotated[PomodoroStatus | None, Query(alias="status")] = None,
    started_from: datetime | None = None,
    started_to: datetime | None = None,
) -> list[PomodoroSessionRead]:
    pomodoro_sessions = list_pomodoro_sessions(
        db,
        user_id=current_user.id,
        subject_id=subject_id,
        task_id=task_id,
        status=status_filter,
        started_from=started_from,
        started_to=started_to,
    )
    return [PomodoroSessionRead.model_validate(pomodoro_session) for pomodoro_session in pomodoro_sessions]


@router.get("/{pomodoro_session_id}", response_model=PomodoroSessionRead)
def get_pomodoro_session_endpoint(
    pomodoro_session_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> PomodoroSessionRead:
    pomodoro_session = get_pomodoro_session(db, user_id=current_user.id, pomodoro_session_id=pomodoro_session_id)
    if pomodoro_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pomodoro session not found.")
    return PomodoroSessionRead.model_validate(pomodoro_session)


@router.patch("/{pomodoro_session_id}", response_model=PomodoroSessionRead)
def update_pomodoro_session_endpoint(
    pomodoro_session_id: UUID,
    payload: PomodoroSessionUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> PomodoroSessionRead:
    try:
        pomodoro_session = update_pomodoro_session(
            db,
            user_id=current_user.id,
            pomodoro_session_id=pomodoro_session_id,
            payload=payload,
        )
    except (CrossEntityValidationError, PomodoroStateError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if pomodoro_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pomodoro session not found.")
    return PomodoroSessionRead.model_validate(pomodoro_session)


@router.post("/{pomodoro_session_id}/complete", response_model=PomodoroSessionRead)
def complete_pomodoro_session_endpoint(
    pomodoro_session_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    payload: PomodoroCompleteRequest | None = None,
) -> PomodoroSessionRead:
    try:
        pomodoro_session = complete_pomodoro_session(
            db,
            user_id=current_user.id,
            pomodoro_session_id=pomodoro_session_id,
            payload=payload,
        )
    except PomodoroStateError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if pomodoro_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pomodoro session not found.")
    return PomodoroSessionRead.model_validate(pomodoro_session)
