from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.subjects.models import Subject
from app.modules.subjects.schemas import SubjectUpdate
from app.modules.events.service import service as event_service


class DuplicateSubjectNameError(ValueError):
    pass


def create_subject(
    db: Session,
    *,
    user_id: UUID,
    name: str,
    description: str | None,
    color: str | None,
    term: str | None,
    exam_date,
    credit_hours,
) -> Subject:
    subject = Subject(
        user_id=user_id,
        name=name,
        description=description,
        color=color,
        term=term,
        exam_date=exam_date,
        credit_hours=credit_hours,
    )
    db.add(subject)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateSubjectNameError("Subject name already exists.") from exc
    db.refresh(subject)
    
    event_service.track_subject_created(db=db, user_id=user_id, subject_id=subject.id)
    
    return subject


def list_subjects(db: Session, *, user_id: UUID) -> list[Subject]:
    stmt = select(Subject).where(Subject.user_id == user_id).order_by(Subject.created_at.desc())
    return list(db.scalars(stmt).all())


def get_subject(db: Session, *, user_id: UUID, subject_id: UUID) -> Subject | None:
    stmt = select(Subject).where(Subject.id == subject_id, Subject.user_id == user_id)
    return db.scalar(stmt)


def update_subject(
    db: Session,
    *,
    user_id: UUID,
    subject_id: UUID,
    payload: SubjectUpdate,
) -> Subject | None:
    subject = get_subject(db, user_id=user_id, subject_id=subject_id)
    if subject is None:
        return None

    updates = payload.model_dump(exclude_unset=True)
    for field_name, value in updates.items():
        setattr(subject, field_name, value)

    if not updates:
        return subject

    db.add(subject)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateSubjectNameError("Subject name already exists.") from exc
    db.refresh(subject)
    return subject
