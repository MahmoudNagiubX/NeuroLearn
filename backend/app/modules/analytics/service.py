from uuid import UUID

from sqlalchemy.orm import Session

from app.modules.analytics import schemas
from app.modules.analytics.repository import repository


class AnalyticsService:
    @staticmethod
    def _ensure_user_id(user_id: UUID) -> UUID:
        if isinstance(user_id, UUID):
            return user_id
        raise TypeError(
            "AnalyticsService expected user_id to be a UUID scalar. "
            f"Received {type(user_id).__name__}."
        )

    def get_dashboard_summary(self, db: Session, user_id: UUID) -> schemas.DashboardSummary:
        user_id = self._ensure_user_id(user_id)
        total_study_minutes = repository.get_total_study_minutes(db, user_id)
        weekly_study_minutes = repository.get_weekly_study_minutes(db, user_id)

        completed_tasks = repository.get_completed_tasks(db, user_id)
        total_tasks = repository.get_total_tasks(db, user_id)
        task_completion_rate = round((completed_tasks / total_tasks) * 100, 2) if total_tasks > 0 else 0.0

        pomodoro_sessions = repository.get_pomodoro_sessions(db, user_id)
        notes_created = repository.get_notes_created(db, user_id)
        subjects_studied = repository.get_subjects_studied(db, user_id)

        study_time_series = [schemas.DailyStudyPoint(**d) for d in repository.get_daily_study_minutes(db, user_id)]
        subject_distribution = [schemas.SubjectDistributionPoint(**d) for d in repository.get_subject_distribution(db, user_id)]
        productivity_trend = [schemas.ProductivityPoint(**d) for d in repository.get_productivity_trend(db, user_id)]
        recent_activity = [schemas.RecentActivityItem(**d) for d in repository.get_recent_activity(db, user_id)]

        return schemas.DashboardSummary(
            total_study_minutes=total_study_minutes,
            weekly_study_minutes=weekly_study_minutes,
            completed_tasks=completed_tasks,
            task_completion_rate=task_completion_rate,
            pomodoro_sessions=pomodoro_sessions,
            notes_created=notes_created,
            subjects_studied=subjects_studied,
            study_time_series=study_time_series,
            subject_distribution=subject_distribution,
            productivity_trend=productivity_trend,
            recent_activity=recent_activity,
        )

    def get_study_time_series(self, db: Session, user_id: UUID) -> list[schemas.DailyStudyPoint]:
        user_id = self._ensure_user_id(user_id)
        return [schemas.DailyStudyPoint(**d) for d in repository.get_daily_study_minutes(db, user_id)]

    def get_subject_distribution(self, db: Session, user_id: UUID) -> list[schemas.SubjectDistributionPoint]:
        user_id = self._ensure_user_id(user_id)
        return [schemas.SubjectDistributionPoint(**d) for d in repository.get_subject_distribution(db, user_id)]

    def get_productivity_trend(self, db: Session, user_id: UUID) -> list[schemas.ProductivityPoint]:
        user_id = self._ensure_user_id(user_id)
        return [schemas.ProductivityPoint(**d) for d in repository.get_productivity_trend(db, user_id)]

    def get_recent_activity(self, db: Session, user_id: UUID) -> list[schemas.RecentActivityItem]:
        user_id = self._ensure_user_id(user_id)
        return [schemas.RecentActivityItem(**d) for d in repository.get_recent_activity(db, user_id)]


service = AnalyticsService()
