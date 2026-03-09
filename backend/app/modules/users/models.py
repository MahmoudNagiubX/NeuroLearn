from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, String, func, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.base import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("length(trim(email)) > 0", name="chk_users_email_not_blank"),
    )

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String, nullable=True)
    is_email_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
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

    settings: Mapped[UserSettings | None] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )


class UserSettings(Base):
    __tablename__ = "user_settings"
    __table_args__ = (
        CheckConstraint("daily_study_goal_minutes > 0"),
        CheckConstraint("pomodoro_focus_minutes > 0"),
        CheckConstraint("pomodoro_break_minutes >= 0"),
        CheckConstraint("pomodoro_long_break_minutes >= 0"),
        CheckConstraint("pomodoro_sessions_before_long_break > 0"),
    )

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    timezone: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'Africa/Cairo'"))
    daily_study_goal_minutes: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("120"))
    pomodoro_focus_minutes: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("25"))
    pomodoro_break_minutes: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("5"))
    pomodoro_long_break_minutes: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("15"))
    pomodoro_sessions_before_long_break: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("4"),
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

    user: Mapped[User] = relationship(back_populates="settings")
