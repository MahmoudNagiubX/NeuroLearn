from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.modules.study_sessions.models import StudySession, StudySessionStatus
from app.modules.tasks.models import Task, TaskStatus
from app.modules.pomodoro.models import PomodoroSession, PomodoroStatus
from app.modules.notes.models import Note
from app.modules.subjects.models import Subject
from app.modules.events.models import AppEvent


class AnalyticsRepository:
    @staticmethod
    def _ensure_user_id(user_id: UUID) -> UUID:
        if isinstance(user_id, UUID):
            return user_id
        raise TypeError(
            "AnalyticsRepository expected user_id to be a UUID scalar. "
            f"Received {type(user_id).__name__}."
        )

    # ------------------------------------------------------------------
    # Existing KPI queries (bugfix: actual_duration_minutes not duration_minutes)
    # ------------------------------------------------------------------

    def get_total_study_minutes(self, db: Session, user_id: UUID) -> int:
        user_id = self._ensure_user_id(user_id)
        stmt = select(func.coalesce(func.sum(StudySession.actual_duration_minutes), 0)).where(
            and_(
                StudySession.user_id == user_id,
                StudySession.status == StudySessionStatus.COMPLETED,
            )
        )
        return db.scalar(stmt) or 0

    def get_weekly_study_minutes(self, db: Session, user_id: UUID) -> int:
        user_id = self._ensure_user_id(user_id)
        start_of_week = datetime.now(timezone.utc) - timedelta(days=7)
        stmt = select(func.coalesce(func.sum(StudySession.actual_duration_minutes), 0)).where(
            and_(
                StudySession.user_id == user_id,
                StudySession.status == StudySessionStatus.COMPLETED,
                StudySession.completed_at >= start_of_week,
            )
        )
        return db.scalar(stmt) or 0

    def get_completed_tasks(self, db: Session, user_id: UUID) -> int:
        user_id = self._ensure_user_id(user_id)
        stmt = select(func.count(Task.id)).where(
            and_(
                Task.user_id == user_id,
                Task.status == TaskStatus.DONE,
            )
        )
        return db.scalar(stmt) or 0

    def get_total_tasks(self, db: Session, user_id: UUID) -> int:
        user_id = self._ensure_user_id(user_id)
        stmt = select(func.count(Task.id)).where(Task.user_id == user_id)
        return db.scalar(stmt) or 0

    def get_pomodoro_sessions(self, db: Session, user_id: UUID) -> int:
        user_id = self._ensure_user_id(user_id)
        stmt = select(func.count(PomodoroSession.id)).where(
            and_(
                PomodoroSession.user_id == user_id,
                PomodoroSession.status == PomodoroStatus.COMPLETED,
            )
        )
        return db.scalar(stmt) or 0

    def get_notes_created(self, db: Session, user_id: UUID) -> int:
        user_id = self._ensure_user_id(user_id)
        stmt = select(func.count(Note.id)).where(Note.user_id == user_id)
        return db.scalar(stmt) or 0

    def get_subjects_studied(self, db: Session, user_id: UUID) -> int:
        user_id = self._ensure_user_id(user_id)
        stmt = select(func.count(func.distinct(StudySession.subject_id))).where(
            and_(
                StudySession.user_id == user_id,
                StudySession.subject_id.is_not(None),
                StudySession.status == StudySessionStatus.COMPLETED,
            )
        )
        return db.scalar(stmt) or 0

    # ------------------------------------------------------------------
    # 6.4 — New behavioral metric queries
    # ------------------------------------------------------------------

    def get_daily_study_minutes(self, db: Session, user_id: UUID) -> list[dict]:
        """
        Group completed study sessions by calendar date (UTC).
        Returns a list of {date: str, study_minutes: int} dicts.
        """
        user_id = self._ensure_user_id(user_id)
        rows = (
            db.query(
                func.date(StudySession.completed_at).label("day"),
                func.coalesce(func.sum(StudySession.actual_duration_minutes), 0).label("study_minutes"),
            )
            .filter(
                StudySession.user_id == user_id,
                StudySession.status == StudySessionStatus.COMPLETED,
                StudySession.completed_at.is_not(None),
            )
            .group_by(func.date(StudySession.completed_at))
            .order_by(func.date(StudySession.completed_at))
            .all()
        )
        return [{"date": str(r.day), "study_minutes": int(r.study_minutes)} for r in rows]

    def get_subject_distribution(self, db: Session, user_id: UUID) -> list[dict]:
        """
        Total completed study minutes per subject (with subject name).
        Returns a list of {subject_id, subject_name, total_minutes}.
        """
        user_id = self._ensure_user_id(user_id)
        rows = (
            db.query(
                StudySession.subject_id,
                Subject.name.label("subject_name"),
                func.coalesce(func.sum(StudySession.actual_duration_minutes), 0).label("total_minutes"),
            )
            .outerjoin(Subject, Subject.id == StudySession.subject_id)
            .filter(
                StudySession.user_id == user_id,
                StudySession.status == StudySessionStatus.COMPLETED,
                StudySession.subject_id.is_not(None),
            )
            .group_by(StudySession.subject_id, Subject.name)
            .order_by(func.sum(StudySession.actual_duration_minutes).desc())
            .all()
        )
        return [
            {
                "subject_id": str(r.subject_id),
                "subject_name": r.subject_name or "Unknown",
                "total_minutes": int(r.total_minutes),
            }
            for r in rows
        ]

    def get_productivity_trend(self, db: Session, user_id: UUID) -> list[dict]:
        """
        Per-day metrics for the last 7 days (inclusive of today).
        Returns a list of {date, study_minutes, completed_tasks, pomodoro_sessions}.
        """
        user_id = self._ensure_user_id(user_id)
        today = datetime.now(timezone.utc).date()
        days = [(today - timedelta(days=i)) for i in range(6, -1, -1)]

        # Fetch aggregates – we'll merge in Python
        start_dt = datetime.combine(days[0], datetime.min.time()).replace(tzinfo=timezone.utc)

        study_rows = (
            db.query(
                func.date(StudySession.completed_at).label("day"),
                func.coalesce(func.sum(StudySession.actual_duration_minutes), 0).label("study_minutes"),
            )
            .filter(
                StudySession.user_id == user_id,
                StudySession.status == StudySessionStatus.COMPLETED,
                StudySession.completed_at >= start_dt,
            )
            .group_by(func.date(StudySession.completed_at))
            .all()
        )
        study_map = {str(r.day): int(r.study_minutes) for r in study_rows}

        task_rows = (
            db.query(
                func.date(Task.completed_at).label("day"),
                func.count(Task.id).label("completed_tasks"),
            )
            .filter(
                Task.user_id == user_id,
                Task.status == TaskStatus.DONE,
                Task.completed_at >= start_dt,
            )
            .group_by(func.date(Task.completed_at))
            .all()
        )
        task_map = {str(r.day): int(r.completed_tasks) for r in task_rows}

        pomo_rows = (
            db.query(
                func.date(PomodoroSession.ended_at).label("day"),
                func.count(PomodoroSession.id).label("count"),
            )
            .filter(
                PomodoroSession.user_id == user_id,
                PomodoroSession.status == PomodoroStatus.COMPLETED,
                PomodoroSession.ended_at >= start_dt,
            )
            .group_by(func.date(PomodoroSession.ended_at))
            .all()
        )
        pomo_map = {str(r.day): int(r.count) for r in pomo_rows}

        result = []
        for day in days:
            day_str = str(day)
            result.append(
                {
                    "date": day_str,
                    "study_minutes": study_map.get(day_str, 0),
                    "completed_tasks": task_map.get(day_str, 0),
                    "pomodoro_sessions": pomo_map.get(day_str, 0),
                }
            )
        return result

    def get_recent_activity(self, db: Session, user_id: UUID, limit: int = 10) -> list[dict]:
        """
        Last N events for the user from app_events.
        Returns a list of {event_type, occurred_at, entity_type, entity_id}.
        """
        user_id = self._ensure_user_id(user_id)
        rows = (
            db.query(
                AppEvent.event_type,
                AppEvent.occurred_at,
                AppEvent.entity_type,
                AppEvent.entity_id,
            )
            .filter(AppEvent.user_id == user_id)
            .order_by(AppEvent.occurred_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "event_type": r.event_type,
                "occurred_at": r.occurred_at.isoformat(),
                "entity_type": r.entity_type,
                "entity_id": str(r.entity_id) if r.entity_id else None,
            }
            for r in rows
        ]


repository = AnalyticsRepository()
