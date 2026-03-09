from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps.auth_dependencies import get_current_user
from app.core.database.session import get_db
from app.modules.subjects.schemas import SubjectCreate, SubjectRead, SubjectUpdate
from app.modules.subjects.service import (
    DuplicateSubjectNameError,
    create_subject,
    get_subject,
    list_subjects,
    update_subject,
)
from app.modules.users.models import User


router = APIRouter(prefix="/subjects", tags=["subjects"])


@router.post("", response_model=SubjectRead, status_code=status.HTTP_201_CREATED)
def create_subject_endpoint(
    payload: SubjectCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> SubjectRead:
    try:
        subject = create_subject(
            db,
            user_id=current_user.id,
            name=payload.name,
            description=payload.description,
            color=payload.color,
            term=payload.term,
            exam_date=payload.exam_date,
            credit_hours=payload.credit_hours,
        )
    except DuplicateSubjectNameError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return SubjectRead.model_validate(subject)


@router.get("", response_model=list[SubjectRead])
def list_subjects_endpoint(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[SubjectRead]:
    subjects = list_subjects(db, user_id=current_user.id)
    return [SubjectRead.model_validate(subject) for subject in subjects]


@router.get("/{subject_id}", response_model=SubjectRead)
def get_subject_endpoint(
    subject_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> SubjectRead:
    subject = get_subject(db, user_id=current_user.id, subject_id=subject_id)
    if subject is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found.")
    return SubjectRead.model_validate(subject)


@router.patch("/{subject_id}", response_model=SubjectRead)
def update_subject_endpoint(
    subject_id: UUID,
    payload: SubjectUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> SubjectRead:
    try:
        subject = update_subject(
            db,
            user_id=current_user.id,
            subject_id=subject_id,
            payload=payload,
        )
    except DuplicateSubjectNameError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    if subject is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found.")

    return SubjectRead.model_validate(subject)
