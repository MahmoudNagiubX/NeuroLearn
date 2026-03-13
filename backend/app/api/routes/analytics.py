from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps.auth_dependencies import get_current_user_id
from app.core.database.session import get_db
from app.modules.analytics import schemas
from app.modules.analytics.service import service

router = APIRouter()


@router.get("/dashboard", response_model=schemas.DashboardSummary)
def read_dashboard(
    db: Annotated[Session, Depends(get_db)],
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> Any:
    """Full dashboard summary including all series."""
    return service.get_dashboard_summary(db=db, user_id=current_user_id)


@router.get("/study-time-series", response_model=list[schemas.DailyStudyPoint])
def read_study_time_series(
    db: Annotated[Session, Depends(get_db)],
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> Any:
    """Daily study minutes time series."""
    return service.get_study_time_series(db=db, user_id=current_user_id)


@router.get("/subjects", response_model=list[schemas.SubjectDistributionPoint])
def read_subject_distribution(
    db: Annotated[Session, Depends(get_db)],
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> Any:
    """Study time distribution by subject."""
    return service.get_subject_distribution(db=db, user_id=current_user_id)


@router.get("/productivity-trend", response_model=list[schemas.ProductivityPoint])
def read_productivity_trend(
    db: Annotated[Session, Depends(get_db)],
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> Any:
    """7-day productivity trend (study, tasks, pomodoro per day)."""
    return service.get_productivity_trend(db=db, user_id=current_user_id)


@router.get("/recent-activity", response_model=list[schemas.RecentActivityItem])
def read_recent_activity(
    db: Annotated[Session, Depends(get_db)],
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> Any:
    """Last 10 user events from app_events."""
    return service.get_recent_activity(db=db, user_id=current_user_id)
