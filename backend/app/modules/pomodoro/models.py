from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, Enum as SAEnum, ForeignKey, Integer, String, func, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base


class PomodoroStatus(str, Enum):
    COMPLETED = "completed"
    ABORTED = "aborted"


class PomodoroSessionType(str, Enum):
    FOCUS = "focus"
    SHORT_BREAK = "short_break"
    LONG_BREAK = "long_break"


pomodoro_status_enum = SAEnum(
    PomodoroStatus,
    name="pomodoro_status",
    values_callable=lambda enum_cls: [item.value for item in enum_cls],
)

pomodoro_session_type_enum = SAEnum(
    PomodoroSessionType,
    name="pomodoro_session_type",
    values_callable=lambda enum_cls: [item.value for item in enum_cls],
)


class PomodoroSession(Base):
    __tablename__ = "pomodoro_sessions"
    __table_args__ = (
        CheckConstraint("planned_minutes > 0"),
        CheckConstraint("actual_minutes IS NULL OR actual_minutes >= 0"),
        CheckConstraint("focus_minutes IS NULL OR focus_minutes >= 0"),
        CheckConstraint("break_minutes IS NULL OR break_minutes >= 0"),
        CheckConstraint("interruptions >= 0"),
        CheckConstraint("distraction_count >= 0"),
        CheckConstraint("ended_at > started_at", name="chk_pomodoro_sessions_time_window"),
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
    task_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="SET NULL"),
        nullable=True,
    )
    study_session_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("study_sessions.id", ondelete="SET NULL"),
        nullable=True,
    )
    session_type: Mapped[PomodoroSessionType] = mapped_column(
        pomodoro_session_type_enum,
        nullable=False,
        server_default=text("'focus'"),
    )
    planned_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    actual_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    focus_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    break_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    interruptions: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    distraction_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    abandon_reason: Mapped[str | None] = mapped_column(String, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[PomodoroStatus] = mapped_column(
        pomodoro_status_enum,
        nullable=False,
        server_default=text("'completed'"),
    )
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
