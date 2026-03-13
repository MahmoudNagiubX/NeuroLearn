from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from fastapi.testclient import TestClient


def _new_user_payload() -> dict[str, str]:
    suffix = uuid4().hex[:12]
    return {
        "email": f"flow-{suffix}@example.com",
        "password": "Password123!",
        "full_name": "Flow User",
    }


def _signup_and_token(client: TestClient) -> tuple[str, UUID]:
    payload = _new_user_payload()
    response = client.post("/auth/signup", json=payload)
    assert response.status_code == 201
    data = response.json()
    return data["access_token"], UUID(data["user"]["id"])


def _auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_core_flows_and_event_tracking(client: TestClient) -> None:
    token, _ = _signup_and_token(client)
    headers = _auth_header(token)

    create_subject_response = client.post(
        "/subjects",
        headers=headers,
        json={"name": f"Flow Subject {uuid4().hex[:6]}", "description": "Flow subject"},
    )
    assert create_subject_response.status_code == 201
    subject_id = create_subject_response.json()["id"]

    list_subjects_response = client.get("/subjects", headers=headers)
    assert list_subjects_response.status_code == 200
    assert any(subject["id"] == subject_id for subject in list_subjects_response.json())

    create_task_response = client.post(
        "/tasks",
        headers=headers,
        json={
            "title": "Flow task",
            "description": "Flow description",
            "subject_id": subject_id,
        },
    )
    assert create_task_response.status_code == 201
    task_id = create_task_response.json()["id"]

    list_tasks_response = client.get("/tasks", headers=headers)
    assert list_tasks_response.status_code == 200
    assert any(task["id"] == task_id for task in list_tasks_response.json())

    now = datetime.now(timezone.utc)
    create_study_response = client.post(
        "/study-sessions",
        headers=headers,
        json={
            "title": "Flow study session",
            "subject_id": subject_id,
            "task_id": task_id,
            "scheduled_start": (now + timedelta(minutes=5)).isoformat(),
            "scheduled_end": (now + timedelta(minutes=65)).isoformat(),
        },
    )
    assert create_study_response.status_code == 201
    study_session_id = create_study_response.json()["id"]

    start_study_response = client.post(f"/study-sessions/{study_session_id}/start", headers=headers)
    assert start_study_response.status_code == 200

    complete_study_response = client.post(
        f"/study-sessions/{study_session_id}/complete",
        headers=headers,
        json={"actual_duration_minutes": 50},
    )
    assert complete_study_response.status_code == 200

    create_pomodoro_response = client.post(
        "/pomodoro-sessions",
        headers=headers,
        json={
            "subject_id": subject_id,
            "task_id": task_id,
            "study_session_id": study_session_id,
            "planned_minutes": 25,
            "status": "aborted",
        },
    )
    assert create_pomodoro_response.status_code == 201
    pomodoro_id = create_pomodoro_response.json()["id"]

    complete_pomodoro_response = client.post(
        f"/pomodoro-sessions/{pomodoro_id}/complete",
        headers=headers,
    )
    assert complete_pomodoro_response.status_code == 200

    list_pomodoro_response = client.get("/pomodoro-sessions", headers=headers)
    assert list_pomodoro_response.status_code == 200
    assert any(session["id"] == pomodoro_id for session in list_pomodoro_response.json())

    dashboard_response = client.get("/analytics/dashboard", headers=headers)
    assert dashboard_response.status_code == 200
    dashboard_payload = dashboard_response.json()
    assert dashboard_payload["total_study_minutes"] >= 50
    assert isinstance(dashboard_payload["recent_activity"], list)

    events_response = client.get("/events", headers=headers)
    assert events_response.status_code == 200
    events_payload = events_response.json()
    event_types = {event["event_type"] for event in events_payload}
    assert {
        "SUBJECT_CREATED",
        "TASK_CREATED",
        "STUDY_SESSION_STARTED",
        "STUDY_SESSION_COMPLETED",
        "POMODORO_STARTED",
        "POMODORO_COMPLETED",
    }.issubset(event_types)
