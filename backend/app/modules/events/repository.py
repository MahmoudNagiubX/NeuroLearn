from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.events.models import AppEvent
from app.modules.events.schemas import EventCreate


class EventRepository:
    def create_event(self, db: Session, event_data: EventCreate) -> AppEvent:
        db_event = AppEvent(**event_data.model_dump())
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
