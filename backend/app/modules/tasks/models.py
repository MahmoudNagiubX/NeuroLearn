from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.base import Base


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    ARCHIVED = "archived"


task_status_enum = SAEnum(
    TaskStatus,
    name="task_status",
    values_callable=lambda enum_cls: [item.value for item in enum_cls],
)


class TaskList(Base):
    __tablename__ = "task_lists"
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_task_lists_user_name"),
        CheckConstraint("length(trim(name)) > 0", name="chk_task_lists_name_not_blank"),
    )

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    tasks: Mapped[list["Task"]] = relationship(back_populates="task_list")


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (
        CheckConstraint("length(trim(title)) > 0", name="chk_tasks_title_not_blank"),
        CheckConstraint(
            "(is_recurring = FALSE AND recurrence_rule IS NULL) OR "
            "(is_recurring = TRUE AND recurrence_rule IS NOT NULL)",
            name="chk_tasks_recurrence_consistency",
        ),
        CheckConstraint("(status <> 'done') OR completed_at IS NOT NULL", name="chk_tasks_completed_status"),
        CheckConstraint("archived_at IS NULL OR status = 'archived'", name="chk_tasks_archived_status"),
        CheckConstraint("priority BETWEEN 1 AND 5"),
        CheckConstraint("estimated_minutes IS NULL OR estimated_minutes > 0"),
    )

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    subject_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("subjects.id", ondelete="SET NULL"),
        nullable=True,
    )
    list_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("task_lists.id", ondelete="SET NULL"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(
        task_status_enum,
        nullable=False,
        server_default=text("'todo'"),
    )
    priority: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default=text("3"))
    position: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reminder_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    estimated_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_recurring: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )
    recurrence_rule: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    subject: Mapped["Subject | None"] = relationship("Subject", back_populates="tasks")
    task_list: Mapped["TaskList | None"] = relationship("TaskList", back_populates="tasks")
    tags: Mapped[list["Tag"]] = relationship(
        secondary="task_tags",
        back_populates="tasks",
    )


class Tag(Base):
    __tablename__ = "tags"
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_tags_user_name"),
        CheckConstraint("length(trim(name)) > 0", name="chk_tags_name_not_blank"),
    )

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    tasks: Mapped[list["Task"]] = relationship(
        secondary="task_tags",
        back_populates="tags",
    )


class TaskTag(Base):
    __tablename__ = "task_tags"

    task_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        primary_key=True,
    )
    tag_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
    )
