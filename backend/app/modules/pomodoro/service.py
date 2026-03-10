from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.pomodoro.models import PomodoroSession, PomodoroStatus
from app.modules.pomodoro.schemas import PomodoroCompleteRequest, PomodoroSessionCreate, PomodoroSessionUpdate
from app.modules.study_sessions.models import StudySession
from app.modules.subjects.models import Subject
from app.modules.tasks.models import Task
from app.modules.events.service import service as event_service


class CrossEntityValidationError(ValueError):
    pass


class PomodoroStateError(ValueError):
    pass


def _validate_time_window(started_at: datetime, ended_at: datetime) -> None:
    if ended_at <= started_at:
        raise PomodoroStateError("ended_at must be after started_at.")


def _validate_links(
    db: Session,
    *,
    user_id: UUID,
    subject_id: UUID | None,
    task_id: UUID | None,
    study_session_id: UUID | None,
) -> None:
    task: Task | None = None
    study_session: StudySession | None = None

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

    if study_session_id is not None:
        study_session = db.scalar(
            select(StudySession).where(StudySession.id == study_session_id, StudySession.user_id == user_id)
        )
        if study_session is None:
            raise CrossEntityValidationError("study_session_id does not belong to current user.")

    if subject_id is not None and task is not None and task.subject_id is not None and task.subject_id != subject_id:
        raise CrossEntityValidationError("task_id does not belong to the provided subject_id.")

    if study_session is not None and task_id is not None and study_session.task_id is not None:
        if study_session.task_id != task_id:
            raise CrossEntityValidationError("task_id does not match study_session_id.")

    if study_session is not None and subject_id is not None and study_session.subject_id is not None:
        if study_session.subject_id != subject_id:
            raise CrossEntityValidationError("subject_id does not match study_session_id.")


def create_pomodoro_session(db: Session, *, user_id: UUID, payload: PomodoroSessionCreate) -> PomodoroSession:
    started_at = payload.started_at or datetime.now(timezone.utc)
    ended_at = payload.ended_at or (started_at + timedelta(minutes=payload.planned_minutes))
    _validate_time_window(started_at, ended_at)
    _validate_links(
        db,
        user_id=user_id,
        subject_id=payload.subject_id,
        task_id=payload.task_id,
        study_session_id=payload.study_session_id,
    )

    pomodoro_session = PomodoroSession(
        user_id=user_id,
        subject_id=payload.subject_id,
        task_id=payload.task_id,
        study_session_id=payload.study_session_id,
        session_type=payload.session_type,
        planned_minutes=payload.planned_minutes,
        actual_minutes=payload.actual_minutes,
        focus_minutes=payload.focus_minutes,
        break_minutes=payload.break_minutes,
        interruptions=payload.interruptions,
        distraction_count=payload.distraction_count,
        abandon_reason=payload.abandon_reason,
        started_at=started_at,
        ended_at=ended_at,
        status=payload.status,
    )

    if pomodoro_session.actual_minutes is None:
        minutes = int((pomodoro_session.ended_at - pomodoro_session.started_at).total_seconds() // 60)
        pomodoro_session.actual_minutes = max(minutes, 0)

    db.add(pomodoro_session)
    db.commit()
    db.refresh(pomodoro_session)
    
    event_service.track_pomodoro_started(db=db, user_id=user_id, pomodoro_session_id=pomodoro_session.id)
    
    return pomodoro_session


def list_pomodoro_sessions(
    db: Session,
    *,
    user_id: UUID,
    subject_id: UUID | None = None,
    task_id: UUID | None = None,
    status: PomodoroStatus | None = None,
    started_from: datetime | None = None,
    started_to: datetime | None = None,
) -> list[PomodoroSession]:
    stmt = select(PomodoroSession).where(PomodoroSession.user_id == user_id)
    if subject_id is not None:
        stmt = stmt.where(PomodoroSession.subject_id == subject_id)
    if task_id is not None:
        stmt = stmt.where(PomodoroSession.task_id == task_id)
    if status is not None:
        stmt = stmt.where(PomodoroSession.status == status)
    if started_from is not None:
        stmt = stmt.where(PomodoroSession.started_at >= started_from)
    if started_to is not None:
        stmt = stmt.where(PomodoroSession.started_at <= started_to)
    stmt = stmt.order_by(PomodoroSession.started_at.desc())
    return list(db.scalars(stmt).all())


def get_pomodoro_session(db: Session, *, user_id: UUID, pomodoro_session_id: UUID) -> PomodoroSession | None:
    stmt = select(PomodoroSession).where(
        PomodoroSession.id == pomodoro_session_id,
        PomodoroSession.user_id == user_id,
    )
    return db.scalar(stmt)


def update_pomodoro_session(
    db: Session,
    *,
    user_id: UUID,
    pomodoro_session_id: UUID,
    payload: PomodoroSessionUpdate,
) -> PomodoroSession | None:
    pomodoro_session = get_pomodoro_session(db, user_id=user_id, pomodoro_session_id=pomodoro_session_id)
    if pomodoro_session is None:
        return None

    updates = payload.model_dump(exclude_unset=True)

    new_subject_id = updates.get("subject_id", pomodoro_session.subject_id)
    new_task_id = updates.get("task_id", pomodoro_session.task_id)
    new_study_session_id = updates.get("study_session_id", pomodoro_session.study_session_id)
    _validate_links(
        db,
        user_id=user_id,
        subject_id=new_subject_id,
        task_id=new_task_id,
        study_session_id=new_study_session_id,
    )

    new_started_at = updates.get("started_at", pomodoro_session.started_at)
    new_ended_at = updates.get("ended_at", pomodoro_session.ended_at)
    _validate_time_window(new_started_at, new_ended_at)

    for field_name, value in updates.items():
        setattr(pomodoro_session, field_name, value)

    if pomodoro_session.status == PomodoroStatus.COMPLETED and pomodoro_session.actual_minutes is None:
        minutes = int((pomodoro_session.ended_at - pomodoro_session.started_at).total_seconds() // 60)
        pomodoro_session.actual_minutes = max(minutes, 0)

    db.add(pomodoro_session)
    db.commit()
    db.refresh(pomodoro_session)
    return pomodoro_session


def complete_pomodoro_session(
    db: Session,
    *,
    user_id: UUID,
    pomodoro_session_id: UUID,
    payload: PomodoroCompleteRequest | None = None,
) -> PomodoroSession | None:
    pomodoro_session = get_pomodoro_session(db, user_id=user_id, pomodoro_session_id=pomodoro_session_id)
    if pomodoro_session is None:
        return None

    ended_at = payload.ended_at if payload and payload.ended_at is not None else datetime.now(timezone.utc)
    _validate_time_window(pomodoro_session.started_at, ended_at)

    pomodoro_session.ended_at = ended_at
    pomodoro_session.status = PomodoroStatus.COMPLETED

    if payload is not None:
        if payload.actual_minutes is not None:
            pomodoro_session.actual_minutes = payload.actual_minutes
        if payload.focus_minutes is not None:
            pomodoro_session.focus_minutes = payload.focus_minutes
        if payload.break_minutes is not None:
            pomodoro_session.break_minutes = payload.break_minutes
        if payload.interruptions is not None:
            pomodoro_session.interruptions = payload.interruptions
        if payload.distraction_count is not None:
            pomodoro_session.distraction_count = payload.distraction_count
        if payload.abandon_reason is not None:
            pomodoro_session.abandon_reason = payload.abandon_reason

    if pomodoro_session.actual_minutes is None:
        minutes = int((pomodoro_session.ended_at - pomodoro_session.started_at).total_seconds() // 60)
        pomodoro_session.actual_minutes = max(minutes, 0)

    db.add(pomodoro_session)
    db.commit()
    db.refresh(pomodoro_session)
    
    event_service.track_pomodoro_completed(db=db, user_id=user_id, pomodoro_session_id=pomodoro_session.id)
    
    return pomodoro_session
