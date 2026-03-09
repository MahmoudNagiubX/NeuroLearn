from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.study_sessions.models import StudySessionStatus


class StudySessionCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    subject_id: UUID | None = None
    task_id: UUID | None = None
    title: str | None = None
    scheduled_start: datetime
    scheduled_end: datetime
    planned_duration_minutes: int | None = Field(default=None, gt=0)
    notes: str | None = None
    summary: str | None = None


class StudySessionUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    subject_id: UUID | None = None
    task_id: UUID | None = None
    title: str | None = None
    scheduled_start: datetime | None = None
    scheduled_end: datetime | None = None
    planned_duration_minutes: int | None = Field(default=None, gt=0)
    actual_duration_minutes: int | None = Field(default=None, ge=0)
    focus_rating: int | None = Field(default=None, ge=1, le=5)
    difficulty_rating: int | None = Field(default=None, ge=1, le=5)
    progress_rating: int | None = Field(default=None, ge=1, le=5)
    notes: str | None = None
    summary: str | None = None


class StudySessionCompleteRequest(BaseModel):
    actual_duration_minutes: int | None = Field(default=None, ge=0)
    focus_rating: int | None = Field(default=None, ge=1, le=5)
    difficulty_rating: int | None = Field(default=None, ge=1, le=5)
    progress_rating: int | None = Field(default=None, ge=1, le=5)
    notes: str | None = None
    summary: str | None = None


class StudySessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    subject_id: UUID | None
    task_id: UUID | None
    title: str | None
    scheduled_start: datetime
    scheduled_end: datetime
    started_at: datetime | None
    completed_at: datetime | None
    planned_duration_minutes: int | None
    actual_duration_minutes: int | None
    focus_rating: int | None
    difficulty_rating: int | None
    progress_rating: int | None
    notes: str | None
    summary: str | None
    status: StudySessionStatus
    created_at: datetime
    updated_at: datetime
