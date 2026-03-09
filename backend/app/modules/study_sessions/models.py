from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, Enum as SAEnum, ForeignKey, Integer, SmallInteger, String, func, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base


class StudySessionStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    MISSED = "missed"
    CANCELED = "canceled"


session_status_enum = SAEnum(
    StudySessionStatus,
    name="session_status",
    values_callable=lambda enum_cls: [item.value for item in enum_cls],
)


class StudySession(Base):
    __tablename__ = "study_sessions"
    __table_args__ = (
        CheckConstraint("scheduled_end > scheduled_start", name="chk_study_sessions_schedule_window"),
        CheckConstraint(
            "completed_at IS NULL OR started_at IS NULL OR completed_at >= started_at",
            name="chk_study_sessions_start_before_complete",
        ),
        CheckConstraint("planned_duration_minutes IS NULL OR planned_duration_minutes > 0"),
        CheckConstraint("actual_duration_minutes IS NULL OR actual_duration_minutes >= 0"),
        CheckConstraint("focus_rating IS NULL OR focus_rating BETWEEN 1 AND 5"),
        CheckConstraint("difficulty_rating IS NULL OR difficulty_rating BETWEEN 1 AND 5"),
        CheckConstraint("progress_rating IS NULL OR progress_rating BETWEEN 1 AND 5"),
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
    title: Mapped[str | None] = mapped_column(String, nullable=True)
    scheduled_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    scheduled_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    planned_duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    actual_duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    focus_rating: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    difficulty_rating: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    progress_rating: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)
    summary: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[StudySessionStatus] = mapped_column(
        session_status_enum,
        nullable=False,
        server_default=text("'scheduled'"),
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
