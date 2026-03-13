from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.events.models import AppEvent
from app.modules.events.schemas import EventCreate


class EventRepository:
    _uuid_fields = (
        "user_id",
        "entity_id",
        "subject_id",
        "task_id",
        "study_session_id",
        "pomodoro_session_id",
        "note_id",
    )

    @staticmethod
    def _ensure_uuid_or_none(field_name: str, value: Any) -> UUID | None:
        if value is None:
            return None
        if isinstance(value, UUID):
            return value
        raise TypeError(
            f"EventRepository expected {field_name} to be UUID or None, "
            f"received {type(value).__name__}."
        )

    def _normalize_event_payload(self, event_data: EventCreate) -> dict[str, Any]:
        data: dict[str, Any] = event_data.model_dump()

        raw_metadata = data.pop("metadata", None)
        if raw_metadata is None:
            data["event_metadata"] = {}
        elif isinstance(raw_metadata, dict):
            data["event_metadata"] = raw_metadata
        else:
            raise TypeError(
                "EventRepository expected metadata to be a dictionary."
            )

        for field_name in self._uuid_fields:
            data[field_name] = self._ensure_uuid_or_none(field_name, data.get(field_name))

        return data

    def create_event(self, db: Session, event_data: EventCreate) -> AppEvent:
        data = self._normalize_event_payload(event_data)
        db_event = AppEvent(**data)
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        return db_event

    def get_user_events(
        self, db: Session, user_id: UUID, limit: int = 100
    ) -> list[AppEvent]:
        stmt = (
            select(AppEvent)
            .where(AppEvent.user_id == user_id)
            .order_by(AppEvent.occurred_at.desc())
            .limit(limit)
        )
        result = db.execute(stmt)
        return list(result.scalars().all())

repository = EventRepository()
