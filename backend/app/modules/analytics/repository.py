from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session

from app.modules.study_sessions.models import StudySession
from app.modules.tasks.models import Task, TaskStatus
from app.modules.pomodoro.models import PomodoroSession
from app.modules.notes.models import Note
from app.modules.subjects.models import Subject


class AnalyticsRepository:
    def get_total_study_minutes(self, db: Session, user_id: UUID) -> int:
        stmt = select(func.coalesce(func.sum(StudySession.duration_minutes), 0)).where(
            StudySession.user_id == user_id
        )
        return db.scalar(stmt)

    def get_weekly_study_minutes(self, db: Session, user_id: UUID) -> int:
        start_of_week = datetime.now() - timedelta(days=7)
        stmt = select(func.coalesce(func.sum(StudySession.duration_minutes), 0)).where(
            and_(
                StudySession.user_id == user_id,
                StudySession.created_at >= start_of_week
            )
        )
        return db.scalar(stmt)

    def get_completed_tasks(self, db: Session, user_id: UUID) -> int:
        stmt = select(func.count(Task.id)).where(
            and_(
                Task.user_id == user_id,
                Task.status == TaskStatus.DONE
            )
        )
        return db.scalar(stmt)

    def get_total_tasks(self, db: Session, user_id: UUID) -> int:
        stmt = select(func.count(Task.id)).where(Task.user_id == user_id)
        return db.scalar(stmt)

    def get_pomodoro_sessions(self, db: Session, user_id: UUID) -> int:
        stmt = select(func.count(PomodoroSession.id)).where(PomodoroSession.user_id == user_id)
        return db.scalar(stmt)

    def get_notes_created(self, db: Session, user_id: UUID) -> int:
        stmt = select(func.count(Note.id)).where(Note.user_id == user_id)
        return db.scalar(stmt)

    def get_subjects_studied(self, db: Session, user_id: UUID) -> int:
        stmt = select(func.count(func.distinct(StudySession.subject_id))).where(
            and_(
                StudySession.user_id == user_id,
                StudySession.subject_id.is_not(None)
            )
        )
        return db.scalar(stmt)

repository = AnalyticsRepository()
