from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SubjectCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1)
    description: str | None = None
    color: str | None = None
    term: str | None = None
    exam_date: date | None = None
    credit_hours: Decimal | None = Field(default=None, ge=0)


class SubjectUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=1)
    description: str | None = None
    color: str | None = None
    term: str | None = None
    exam_date: date | None = None
    credit_hours: Decimal | None = Field(default=None, ge=0)
    is_archived: bool | None = None


class SubjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    name: str
    description: str | None
    color: str | None
    term: str | None
    exam_date: date | None
    credit_hours: Decimal | None
    is_archived: bool
    created_at: datetime
    updated_at: datetime
