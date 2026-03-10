from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.modules.events.repository import repository
from app.modules.events.models import AppEvent
from app.modules.events.schemas import EventCreate


class EventService:
    def track_event(self, db: Session, event_data: EventCreate) -> AppEvent:
        return repository.create_event(db, event_data)
        
    def _create_and_track(self, db: Session, user_id: UUID, event_type: str, **kwargs) -> AppEvent:
        event_data = EventCreate(
            user_id=user_id,
            event_type=event_type,
            **kwargs
        )
        return self.track_event(db, event_data)

    def track_task_created(self, db: Session, user_id: UUID, task_id: UUID) -> AppEvent:
        return self._create_and_track(db, user_id, "TASK_CREATED", entity_type="task", entity_id=task_id, task_id=task_id)

    def track_task_completed(self, db: Session, user_id: UUID, task_id: UUID) -> AppEvent:
        return self._create_and_track(db, user_id, "TASK_COMPLETED", entity_type="task", entity_id=task_id, task_id=task_id)

    def track_study_session_started(self, db: Session, user_id: UUID, study_session_id: UUID) -> AppEvent:
        return self._create_and_track(db, user_id, "STUDY_SESSION_STARTED", entity_type="study_session", entity_id=study_session_id, study_session_id=study_session_id)

    def track_study_session_completed(self, db: Session, user_id: UUID, study_session_id: UUID) -> AppEvent:
        return self._create_and_track(db, user_id, "STUDY_SESSION_COMPLETED", entity_type="study_session", entity_id=study_session_id, study_session_id=study_session_id)

    def track_pomodoro_started(self, db: Session, user_id: UUID, pomodoro_session_id: UUID) -> AppEvent:
        return self._create_and_track(db, user_id, "POMODORO_STARTED", entity_type="pomodoro_session", entity_id=pomodoro_session_id, pomodoro_session_id=pomodoro_session_id)

    def track_pomodoro_completed(self, db: Session, user_id: UUID, pomodoro_session_id: UUID) -> AppEvent:
        return self._create_and_track(db, user_id, "POMODORO_COMPLETED", entity_type="pomodoro_session", entity_id=pomodoro_session_id, pomodoro_session_id=pomodoro_session_id)

    def track_note_created(self, db: Session, user_id: UUID, note_id: UUID) -> AppEvent:
        return self._create_and_track(db, user_id, "NOTE_CREATED", entity_type="note", entity_id=note_id, note_id=note_id)

    def track_subject_created(self, db: Session, user_id: UUID, subject_id: UUID) -> AppEvent:
        return self._create_and_track(db, user_id, "SUBJECT_CREATED", entity_type="subject", entity_id=subject_id, subject_id=subject_id)

service = EventService()
