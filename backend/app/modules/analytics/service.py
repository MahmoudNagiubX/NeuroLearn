from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.modules.analytics import schemas
from app.modules.pomodoro.models import PomodoroSession, PomodoroStatus
from app.modules.study_sessions.models import StudySession, StudySessionStatus
from app.modules.subjects.models import Subject
from app.modules.tasks.models import Task, TaskStatus


def get_start_of_today() -> datetime:
    now = datetime.now(timezone.utc)
    return now.replace(hour=0, minute=0, second=0, microsecond=0)


def get_start_of_week() -> datetime:
    now = datetime.now(timezone.utc)
    # 0 = Monday, 6 = Sunday. We go back to Monday.
    start_of_week = now - timedelta(days=now.weekday())
    return start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)


def get_dashboard_metrics(db: Session, user_id: UUID) -> schemas.DashboardMetrics:
    today = get_start_of_today()
    this_week = get_start_of_week()

    # 1. total_study_minutes_today
    study_time_today = db.query(func.coalesce(func.sum(StudySession.actual_duration_minutes), 0).label("minutes")).filter(
        StudySession.user_id == user_id,
        StudySession.status == StudySessionStatus.COMPLETED,
        StudySession.completed_at >= today,
    ).scalar() or 0

    pomodoro_time_today = db.query(func.coalesce(func.sum(PomodoroSession.actual_minutes), 0).label("minutes")).filter(
        PomodoroSession.user_id == user_id,
        PomodoroSession.status == PomodoroStatus.COMPLETED,
        PomodoroSession.ended_at >= today,
    ).scalar() or 0

    total_time_today = study_time_today + pomodoro_time_today

    # 2. study_minutes_this_week
    study_time_week = db.query(func.coalesce(func.sum(StudySession.actual_duration_minutes), 0).label("minutes")).filter(
        StudySession.user_id == user_id,
        StudySession.status == StudySessionStatus.COMPLETED,
        StudySession.completed_at >= this_week,
    ).scalar() or 0

    pomodoro_time_week = db.query(func.coalesce(func.sum(PomodoroSession.actual_minutes), 0).label("minutes")).filter(
        PomodoroSession.user_id == user_id,
        PomodoroSession.status == PomodoroStatus.COMPLETED,
        PomodoroSession.ended_at >= this_week,
    ).scalar() or 0

    total_time_week = study_time_week + pomodoro_time_week

    # 3. tasks_completed_this_week
    tasks_week = db.query(func.count(Task.id)).filter(
        Task.user_id == user_id,
        Task.status == TaskStatus.DONE,
        Task.completed_at >= this_week,
    ).scalar() or 0

    # 4. pomodoro_sessions_today
    pomodoros_today = db.query(func.count(PomodoroSession.id)).filter(
        PomodoroSession.user_id == user_id,
        PomodoroSession.status == PomodoroStatus.COMPLETED,
        PomodoroSession.ended_at >= today,
    ).scalar() or 0

    # 5. subject_study_distribution
    # Aggregate Pomodoro and Study sessions per subject in python for simplicity
    
    distribution_map: dict[str | None, dict[str, Any]] = {}
    
    # StudySessions Subject aggregation
    study_agg = db.query(
        StudySession.subject_id, 
        func.coalesce(func.sum(StudySession.actual_duration_minutes), 0).label("minutes")
    ).filter(
        StudySession.user_id == user_id,
        StudySession.status == StudySessionStatus.COMPLETED,
    ).group_by(StudySession.subject_id).all()

    for row in study_agg:
        subj_id = str(row.subject_id) if row.subject_id else None
        if subj_id not in distribution_map:
            distribution_map[subj_id] = {"subject_id": subj_id, "minutes": 0}
        distribution_map[subj_id]["minutes"] += row.minutes

    # Pomodoro Subject aggregation
    pomo_agg = db.query(
        PomodoroSession.subject_id, 
        func.coalesce(func.sum(PomodoroSession.actual_minutes), 0).label("minutes")
    ).filter(
        PomodoroSession.user_id == user_id,
        PomodoroSession.status == PomodoroStatus.COMPLETED,
    ).group_by(PomodoroSession.subject_id).all()

    for row in pomo_agg:
        subj_id = str(row.subject_id) if row.subject_id else None
        if subj_id not in distribution_map:
            distribution_map[subj_id] = {"subject_id": subj_id, "minutes": 0}
        distribution_map[subj_id]["minutes"] += row.minutes

    # Fetch subject names
    subject_ids = [UUID(k) for k in distribution_map.keys() if k is not None]
    subjects = db.query(Subject).filter(Subject.id.in_(subject_ids)).all() if subject_ids else []
    subject_name_map = {str(s.id): s.name for s in subjects}

    distribution = []
    for k, v in distribution_map.items():
        name = subject_name_map.get(k) if k else "Uncategorized"
        distribution.append(schemas.SubjectDistribution(
            subject_id=k,
            subject_name=name,
            minutes=v["minutes"]
        ))

    return schemas.DashboardMetrics(
        total_study_minutes_today=total_time_today,
        study_minutes_this_week=total_time_week,
        tasks_completed_this_week=tasks_week,
        pomodoro_sessions_today=pomodoros_today,
        subject_study_distribution=distribution,
    )


def get_study_time_metrics(db: Session, user_id: UUID) -> schemas.StudyTimeMetrics:
    dashboard = get_dashboard_metrics(db, user_id)
    return schemas.StudyTimeMetrics(
        total_study_minutes_today=dashboard.total_study_minutes_today,
        study_minutes_this_week=dashboard.study_minutes_this_week,
    )


def get_productivity_metrics(db: Session, user_id: UUID) -> schemas.ProductivityMetrics:
    dashboard = get_dashboard_metrics(db, user_id)
    return schemas.ProductivityMetrics(
        tasks_completed_this_week=dashboard.tasks_completed_this_week,
        pomodoro_sessions_today=dashboard.pomodoro_sessions_today,
    )
