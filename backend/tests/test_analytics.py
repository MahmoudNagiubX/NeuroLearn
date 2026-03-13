from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.core.database.session import SessionLocal
from app.modules.analytics import schemas as analytics_schemas
from app.modules.analytics.service import service as analytics_service
from app.modules.study_sessions.models import StudySession, StudySessionStatus
from app.modules.subjects.models import Subject


DASHBOARD_KEYS = {
    "total_study_minutes",
    "weekly_study_minutes",
    "completed_tasks",
    "task_completion_rate",
    "pomodoro_sessions",
    "notes_created",
    "subjects_studied",
    "study_time_series",
    "subject_distribution",
    "productivity_trend",
    "recent_activity",
}


def _new_user_payload() -> dict[str, str]:
    suffix = uuid4().hex[:12]
    return {
        "email": f"analytics-{suffix}@example.com",
        "password": "Password123!",
        "full_name": "Analytics User",
    }


def _signup_and_token(client: TestClient) -> tuple[str, UUID]:
    payload = _new_user_payload()
    response = client.post("/auth/signup", json=payload)
    assert response.status_code == 201
    data = response.json()
    return data["access_token"], UUID(data["user"]["id"])


def _auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_dashboard_for_user_with_no_sessions_returns_expected_shape(client: TestClient) -> None:
    token, _ = _signup_and_token(client)

    response = client.get("/analytics/dashboard", headers=_auth_header(token))

    assert response.status_code == 200
    payload = response.json()
    assert DASHBOARD_KEYS.issubset(payload.keys())
    assert payload["total_study_minutes"] == 0
    assert payload["weekly_study_minutes"] == 0
    assert payload["completed_tasks"] == 0
    assert payload["task_completion_rate"] == 0.0
    assert payload["study_time_series"] == []
    assert payload["subject_distribution"] == []
    assert payload["recent_activity"] == []
    assert len(payload["productivity_trend"]) == 7


def test_dashboard_for_user_with_study_sessions_returns_aggregates(client: TestClient) -> None:
    token, user_id = _signup_and_token(client)

    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        subject = Subject(user_id=user_id, name=f"Math-{uuid4().hex[:6]}")
        db.add(subject)
        db.flush()

        session = StudySession(
            user_id=user_id,
            subject_id=subject.id,
            title="Session 1",
            scheduled_start=now - timedelta(hours=2),
            scheduled_end=now - timedelta(hours=1, minutes=15),
            started_at=now - timedelta(hours=2),
            completed_at=now - timedelta(hours=1, minutes=15),
            planned_duration_minutes=45,
            actual_duration_minutes=45,
            status=StudySessionStatus.COMPLETED,
        )
        db.add(session)
        db.commit()

    response = client.get("/analytics/dashboard", headers=_auth_header(token))

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_study_minutes"] == 45
    assert payload["weekly_study_minutes"] == 45
    assert payload["subjects_studied"] == 1
    assert any(point["study_minutes"] == 45 for point in payload["study_time_series"])
    assert any(point["total_minutes"] == 45 for point in payload["subject_distribution"])


def test_dashboard_route_passes_scalar_uuid_to_service(client: TestClient, monkeypatch) -> None:
    token, _ = _signup_and_token(client)
    captured: dict[str, object] = {}

    def fake_dashboard_summary(*, db, user_id: UUID) -> analytics_schemas.DashboardSummary:
        captured["user_id"] = user_id
        return analytics_schemas.DashboardSummary(
            total_study_minutes=0,
            weekly_study_minutes=0,
            completed_tasks=0,
            task_completion_rate=0.0,
            pomodoro_sessions=0,
            notes_created=0,
            subjects_studied=0,
            study_time_series=[],
            subject_distribution=[],
            productivity_trend=[],
            recent_activity=[],
        )

    monkeypatch.setattr(analytics_service, "get_dashboard_summary", fake_dashboard_summary)

    response = client.get("/analytics/dashboard", headers=_auth_header(token))

    assert response.status_code == 200
    assert isinstance(captured["user_id"], UUID)
