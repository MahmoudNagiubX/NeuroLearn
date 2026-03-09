from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.tasks.models import TaskStatus


class TaskListCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1)


class TaskListUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1)


class TaskListRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    name: str
    created_at: datetime
    updated_at: datetime


class TagCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1)


class TagRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    name: str
    created_at: datetime
    updated_at: datetime


class TaskCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    subject_id: UUID | None = None
    task_list_id: UUID | None = None
    title: str = Field(min_length=1)
    description: str | None = None
    status: TaskStatus = TaskStatus.TODO
    priority: int = Field(default=3, ge=1, le=5)
    position: int = 0
    due_at: datetime | None = None
    reminder_at: datetime | None = None
    estimated_minutes: int | None = Field(default=None, gt=0)
    is_recurring: bool = False
    recurrence_rule: str | None = None
    tag_ids: list[UUID] = Field(default_factory=list)


class TaskUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    subject_id: UUID | None = None
    task_list_id: UUID | None = None
    title: str | None = Field(default=None, min_length=1)
    description: str | None = None
    status: TaskStatus | None = None
    priority: int | None = Field(default=None, ge=1, le=5)
    position: int | None = None
    due_at: datetime | None = None
    reminder_at: datetime | None = None
    estimated_minutes: int | None = Field(default=None, gt=0)
    is_recurring: bool | None = None
    recurrence_rule: str | None = None
    tag_ids: list[UUID] | None = None


class TaskRead(BaseModel):
    id: UUID
    user_id: UUID
    subject_id: UUID | None
    task_list_id: UUID | None
    title: str
    description: str | None
    status: TaskStatus
    priority: int
    position: int
    due_at: datetime | None
    reminder_at: datetime | None
    estimated_minutes: int | None
    completed_at: datetime | None
    archived_at: datetime | None
    is_recurring: bool
    recurrence_rule: str | None
    tag_ids: list[UUID]
    created_at: datetime
    updated_at: datetime
