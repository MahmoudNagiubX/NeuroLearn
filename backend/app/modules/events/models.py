from __future__ import annotations

from datetime import datetime
from uuid import UUID
from typing import Any

from sqlalchemy import DateTime, ForeignKey, String, func, text, Index
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base


class AppEvent(Base):
    __tablename__ = "app_events"
    
    __table_args__ = (
        Index("idx_events_user", "user_id"),
        Index("idx_events_type", "event_type"),
        Index("idx_events_occurred", "occurred_at"),
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
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    
    entity_type: Mapped[str | None] = mapped_column(String, nullable=True)
    entity_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    
    subject_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    task_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    study_session_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    pomodoro_session_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    note_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    
    metadata: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
