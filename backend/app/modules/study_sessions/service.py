from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.study_sessions.models import StudySession, StudySessionStatus
from app.modules.study_sessions.schemas import StudySessionCompleteRequest, StudySessionCreate, StudySessionUpdate
from app.modules.subjects.models import Subject
from app.modules.tasks.models import Task


class CrossEntityValidationError(ValueError):
    pass


class StudySessionStateError(ValueError):
    pass


def _validate_schedule_window(start: datetime, end: datetime) -> None:
    if end <= start:
        raise StudySessionStateError("scheduled_end must be after scheduled_start.")


def _validate_links(
    db: Session,
    *,
    user_id: UUID,
    subject_id: UUID | None,
    task_id: UUID | None,
) -> None:
    task: Task | None = None

    if subject_id is not None:
        subject_exists = db.scalar(
            select(Subject.id).where(Subject.id == subject_id, Subject.user_id == user_id)
        )
        if subject_exists is None:
            raise CrossEntityValidationError("subject_id does not belong to current user.")

    if task_id is not None:
        task = db.scalar(select(Task).where(Task.id == task_id, Task.user_id == user_id))
        if task is None:
            raise CrossEntityValidationError("task_id does not belong to current user.")

    if subject_id is not None and task is not None and task.subject_id is not None and task.subject_id != subject_id:
        raise CrossEntityValidationError("task_id does not belong to the provided subject_id.")


def create_study_session(db: Session, *, user_id: UUID, payload: StudySessionCreate) -> StudySession:
    _validate_schedule_window(payload.scheduled_start, payload.scheduled_end)
    _validate_links(db, user_id=user_id, subject_id=payload.subject_id, task_id=payload.task_id)

    study_session = StudySession(
        user_id=user_id,
        subject_id=payload.subject_id,
        task_id=payload.task_id,
        title=payload.title,
        scheduled_start=payload.scheduled_start,
        scheduled_end=payload.scheduled_end,
        planned_duration_minutes=payload.planned_duration_minutes,
        notes=payload.notes,
        summary=payload.summary,
        status=StudySessionStatus.SCHEDULED,
    )
    db.add(study_session)
    db.commit()
    db.refresh(study_session)
    return study_session


def list_study_sessions(
    db: Session,
    *,
    user_id: UUID,
    status: StudySessionStatus | None = None,
    subject_id: UUID | None = None,
    task_id: UUID | None = None,
) -> list[StudySession]:
    stmt = select(StudySession).where(StudySession.user_id == user_id)
    if status is not None:
        stmt = stmt.where(StudySession.status == status)
    if subject_id is not None:
        stmt = stmt.where(StudySession.subject_id == subject_id)
    if task_id is not None:
        stmt = stmt.where(StudySession.task_id == task_id)
    stmt = stmt.order_by(StudySession.scheduled_start.desc())
    return list(db.scalars(stmt).all())


def get_study_session(db: Session, *, user_id: UUID, study_session_id: UUID) -> StudySession | None:
    stmt = select(StudySession).where(
        StudySession.id == study_session_id,
        StudySession.user_id == user_id,
    )
    return db.scalar(stmt)


def update_study_session(
    db: Session,
    *,
    user_id: UUID,
    study_session_id: UUID,
    payload: StudySessionUpdate,
) -> StudySession | None:
    study_session = get_study_session(db, user_id=user_id, study_session_id=study_session_id)
    if study_session is None:
        return None

    updates = payload.model_dump(exclude_unset=True)

    new_subject_id = updates.get("subject_id", study_session.subject_id)
    new_task_id = updates.get("task_id", study_session.task_id)
    _validate_links(db, user_id=user_id, subject_id=new_subject_id, task_id=new_task_id)

    new_start = updates.get("scheduled_start", study_session.scheduled_start)
    new_end = updates.get("scheduled_end", study_session.scheduled_end)
    _validate_schedule_window(new_start, new_end)

    for field_name, value in updates.items():
        setattr(study_session, field_name, value)

    db.add(study_session)
    db.commit()
    db.refresh(study_session)
    return study_session


def start_study_session(db: Session, *, user_id: UUID, study_session_id: UUID) -> StudySession | None:
    study_session = get_study_session(db, user_id=user_id, study_session_id=study_session_id)
    if study_session is None:
        return None

    if study_session.status != StudySessionStatus.SCHEDULED:
        raise StudySessionStateError("Only scheduled sessions can be started.")

    study_session.status = StudySessionStatus.IN_PROGRESS
    if study_session.started_at is None:
        study_session.started_at = datetime.now(timezone.utc)

    db.add(study_session)
    db.commit()
    db.refresh(study_session)
    return study_session


def complete_study_session(
    db: Session,
    *,
    user_id: UUID,
    study_session_id: UUID,
    payload: StudySessionCompleteRequest | None = None,
) -> StudySession | None:
    study_session = get_study_session(db, user_id=user_id, study_session_id=study_session_id)
    if study_session is None:
        return None

    if study_session.status not in {StudySessionStatus.SCHEDULED, StudySessionStatus.IN_PROGRESS}:
        raise StudySessionStateError("Only scheduled or in-progress sessions can be completed.")

    now = datetime.now(timezone.utc)
    if study_session.started_at is None:
        study_session.started_at = now
    study_session.completed_at = now
    study_session.status = StudySessionStatus.COMPLETED

    if payload is not None:
        if payload.actual_duration_minutes is not None:
            study_session.actual_duration_minutes = payload.actual_duration_minutes
        if payload.focus_rating is not None:
            study_session.focus_rating = payload.focus_rating
        if payload.difficulty_rating is not None:
            study_session.difficulty_rating = payload.difficulty_rating
        if payload.progress_rating is not None:
            study_session.progress_rating = payload.progress_rating
        if payload.notes is not None:
            study_session.notes = payload.notes
        if payload.summary is not None:
            study_session.summary = payload.summary

    if study_session.actual_duration_minutes is None:
        duration_minutes = int((study_session.completed_at - study_session.started_at).total_seconds() // 60)
        study_session.actual_duration_minutes = max(duration_minutes, 0)

    db.add(study_session)
    db.commit()
    db.refresh(study_session)
    return study_session


def cancel_study_session(db: Session, *, user_id: UUID, study_session_id: UUID) -> StudySession | None:
    study_session = get_study_session(db, user_id=user_id, study_session_id=study_session_id)
    if study_session is None:
        return None

    if study_session.status not in {StudySessionStatus.SCHEDULED, StudySessionStatus.IN_PROGRESS}:
        raise StudySessionStateError("Only scheduled or in-progress sessions can be canceled.")

    study_session.status = StudySessionStatus.CANCELED

    db.add(study_session)
    db.commit()
    db.refresh(study_session)
    return study_session
