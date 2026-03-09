from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, ForeignKey, Numeric, String, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.base import Base


class Subject(Base):
    __tablename__ = "subjects"
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_subjects_user_name"),
        CheckConstraint("length(trim(name)) > 0", name="chk_subjects_name_not_blank"),
        CheckConstraint("credit_hours IS NULL OR credit_hours >= 0"),
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
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    color: Mapped[str | None] = mapped_column(String, nullable=True)
    term: Mapped[str | None] = mapped_column(String, nullable=True)
    exam_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    credit_hours: Mapped[Decimal | None] = mapped_column(Numeric(4, 1), nullable=True)
    is_archived: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
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

    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="subject")

