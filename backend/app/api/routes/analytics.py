import uuid
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps.auth_dependencies import get_current_user
from app.core.database.session import get_db
from app.modules.analytics import schemas, service

router = APIRouter()

@router.get("/dashboard", response_model=schemas.DashboardMetrics)
def read_dashboard(
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user),
) -> Any:
    """
    Get all dashboard metrics for current user.
    """
    return service.get_dashboard_metrics(db=db, user_id=current_user_id)


@router.get("/study-time", response_model=schemas.StudyTimeMetrics)
def read_study_time(
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user),
) -> Any:
    """
    Get study time metrics for current user.
    """
    return service.get_study_time_metrics(db=db, user_id=current_user_id)


@router.get("/productivity", response_model=schemas.ProductivityMetrics)
def read_productivity(
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user),
) -> Any:
    """
    Get productivity metrics for current user.
    """
    return service.get_productivity_metrics(db=db, user_id=current_user_id)
