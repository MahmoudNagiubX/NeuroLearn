from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps.auth_dependencies import get_current_user
from app.core.database.session import get_db
from app.modules.study_sessions.models import StudySessionStatus
from app.modules.study_sessions.schemas import (
    StudySessionCompleteRequest,
    StudySessionCreate,
    StudySessionRead,
    StudySessionUpdate,
)
from app.modules.study_sessions.service import (
    CrossEntityValidationError,
    StudySessionStateError,
    cancel_study_session,
    complete_study_session,
    create_study_session,
    get_study_session,
    list_study_sessions,
    start_study_session,
    update_study_session,
)
from app.modules.users.models import User


router = APIRouter(prefix="/study-sessions", tags=["study-sessions"])


@router.post("", response_model=StudySessionRead, status_code=status.HTTP_201_CREATED)
def create_study_session_endpoint(
    payload: StudySessionCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> StudySessionRead:
    try:
        study_session = create_study_session(db, user_id=current_user.id, payload=payload)
    except (CrossEntityValidationError, StudySessionStateError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return StudySessionRead.model_validate(study_session)


@router.get("", response_model=list[StudySessionRead])
def list_study_sessions_endpoint(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    status_filter: Annotated[StudySessionStatus | None, Query(alias="status")] = None,
    subject_id: UUID | None = None,
    task_id: UUID | None = None,
) -> list[StudySessionRead]:
    study_sessions = list_study_sessions(
        db,
        user_id=current_user.id,
        status=status_filter,
        subject_id=subject_id,
        task_id=task_id,
    )
    return [StudySessionRead.model_validate(study_session) for study_session in study_sessions]


@router.get("/{study_session_id}", response_model=StudySessionRead)
def get_study_session_endpoint(
    study_session_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> StudySessionRead:
    study_session = get_study_session(db, user_id=current_user.id, study_session_id=study_session_id)
    if study_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study session not found.")
    return StudySessionRead.model_validate(study_session)


@router.patch("/{study_session_id}", response_model=StudySessionRead)
def update_study_session_endpoint(
    study_session_id: UUID,
    payload: StudySessionUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> StudySessionRead:
    try:
        study_session = update_study_session(
            db,
            user_id=current_user.id,
            study_session_id=study_session_id,
            payload=payload,
        )
    except (CrossEntityValidationError, StudySessionStateError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if study_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study session not found.")
    return StudySessionRead.model_validate(study_session)


@router.post("/{study_session_id}/start", response_model=StudySessionRead)
def start_study_session_endpoint(
    study_session_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> StudySessionRead:
    try:
        study_session = start_study_session(db, user_id=current_user.id, study_session_id=study_session_id)
    except StudySessionStateError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if study_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study session not found.")
    return StudySessionRead.model_validate(study_session)


@router.post("/{study_session_id}/complete", response_model=StudySessionRead)
def complete_study_session_endpoint(
    study_session_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    payload: StudySessionCompleteRequest | None = None,
) -> StudySessionRead:
    try:
        study_session = complete_study_session(
            db,
            user_id=current_user.id,
            study_session_id=study_session_id,
            payload=payload,
        )
    except StudySessionStateError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if study_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study session not found.")
    return StudySessionRead.model_validate(study_session)


@router.post("/{study_session_id}/cancel", response_model=StudySessionRead)
def cancel_study_session_endpoint(
    study_session_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> StudySessionRead:
    try:
        study_session = cancel_study_session(db, user_id=current_user.id, study_session_id=study_session_id)
    except StudySessionStateError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if study_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study session not found.")
    return StudySessionRead.model_validate(study_session)
