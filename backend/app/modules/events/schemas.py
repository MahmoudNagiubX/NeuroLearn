from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AppEventBase(BaseModel):
    event_type: str = Field(..., max_length=255)
    meta: dict[str, Any] | None = None


class AppEventCreate(AppEventBase):
    pass


class AppEventResponse(AppEventBase):
    id: UUID
    user_id: UUID
    occurred_at: datetime

    model_config = ConfigDict(from_attributes=True)
