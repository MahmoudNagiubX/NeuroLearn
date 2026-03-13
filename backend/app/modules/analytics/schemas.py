from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# ---- Series / sub-schemas ----

class DailyStudyPoint(BaseModel):
    date: str
    study_minutes: int


class SubjectDistributionPoint(BaseModel):
    subject_id: Optional[str]
    subject_name: Optional[str]
    total_minutes: int


class ProductivityPoint(BaseModel):
    date: str
    study_minutes: int
    completed_tasks: int
    pomodoro_sessions: int


class RecentActivityItem(BaseModel):
    event_type: str
    occurred_at: str
    entity_type: Optional[str]
    entity_id: Optional[str]


# ---- Existing schemas kept for backwards compat ----

class SubjectDistribution(BaseModel):
    subject_id: Optional[str]
    subject_name: Optional[str]
    minutes: int


class DashboardMetrics(BaseModel):
    total_study_minutes_today: int
    study_minutes_this_week: int
    tasks_completed_this_week: int
    pomodoro_sessions_today: int
    subject_study_distribution: list[SubjectDistribution]


class StudyTimeMetrics(BaseModel):
    total_study_minutes_today: int
    study_minutes_this_week: int


class ProductivityMetrics(BaseModel):
    tasks_completed_this_week: int
    pomodoro_sessions_today: int


# ---- Main dashboard summary ----

class DashboardSummary(BaseModel):
    total_study_minutes: int
    weekly_study_minutes: int
    completed_tasks: int
    task_completion_rate: float
    pomodoro_sessions: int
    notes_created: int
    subjects_studied: int
    study_time_series: list[DailyStudyPoint]
    subject_distribution: list[SubjectDistributionPoint]
    productivity_trend: list[ProductivityPoint]
    recent_activity: list[RecentActivityItem]
