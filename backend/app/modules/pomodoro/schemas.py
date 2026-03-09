from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.pomodoro.models import PomodoroSessionType, PomodoroStatus


class PomodoroSessionCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    subject_id: UUID | None = None
    task_id: UUID | None = None
    study_session_id: UUID | None = None
    session_type: PomodoroSessionType = PomodoroSessionType.FOCUS
    planned_minutes: int = Field(gt=0)
    started_at: datetime | None = None
    ended_at: datetime | None = None
    actual_minutes: int | None = Field(default=None, ge=0)
    focus_minutes: int | None = Field(default=None, ge=0)
    break_minutes: int | None = Field(default=None, ge=0)
    interruptions: int = Field(default=0, ge=0)
    distraction_count: int = Field(default=0, ge=0)
    abandon_reason: str | None = None
    status: PomodoroStatus = PomodoroStatus.COMPLETED


class PomodoroSessionUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    subject_id: UUID | None = None
    task_id: UUID | None = None
    study_session_id: UUID | None = None
    session_type: PomodoroSessionType | None = None
    planned_minutes: int | None = Field(default=None, gt=0)
    started_at: datetime | None = None
    ended_at: datetime | None = None
    actual_minutes: int | None = Field(default=None, ge=0)
    focus_minutes: int | None = Field(default=None, ge=0)
    break_minutes: int | None = Field(default=None, ge=0)
    interruptions: int | None = Field(default=None, ge=0)
    distraction_count: int | None = Field(default=None, ge=0)
    abandon_reason: str | None = None
    status: PomodoroStatus | None = None


class PomodoroCompleteRequest(BaseModel):
    ended_at: datetime | None = None
    actual_minutes: int | None = Field(default=None, ge=0)
    focus_minutes: int | None = Field(default=None, ge=0)
    break_minutes: int | None = Field(default=None, ge=0)
    interruptions: int | None = Field(default=None, ge=0)
    distraction_count: int | None = Field(default=None, ge=0)
    abandon_reason: str | None = None


class PomodoroSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    subject_id: UUID | None
    task_id: UUID | None
    study_session_id: UUID | None
    session_type: PomodoroSessionType
    planned_minutes: int
    actual_minutes: int | None
    focus_minutes: int | None
    break_minutes: int | None
    interruptions: int
    distraction_count: int
    abandon_reason: str | None
    started_at: datetime
    ended_at: datetime
    status: PomodoroStatus
    created_at: datetime
    updated_at: datetime
