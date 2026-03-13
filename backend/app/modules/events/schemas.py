from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EventBase(BaseModel):
    user_id: UUID
    event_type: str = Field(..., max_length=255)
    entity_type: str | None = None
    entity_id: UUID | None = None
    subject_id: UUID | None = None
    task_id: UUID | None = None
    study_session_id: UUID | None = None
    pomodoro_session_id: UUID | None = None
    note_id: UUID | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class EventCreate(EventBase):
    pass


class EventResponse(EventBase):
    id: UUID
    occurred_at: datetime
    created_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict, alias="event_metadata")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

