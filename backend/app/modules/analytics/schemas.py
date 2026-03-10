from pydantic import BaseModel


class SubjectDistribution(BaseModel):
    subject_id: str | None
    subject_name: str | None
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
