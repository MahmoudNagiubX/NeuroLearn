from __future__ import annotations

from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.deps.auth_dependencies import get_current_user, get_current_user_id
from app.core.database.session import SessionLocal
from app.modules.analytics.repository import repository
from app.modules.analytics.service import service
from app.modules.events.repository import repository as events_repository
from app.modules.users.models import User


def _new_user_payload() -> dict[str, str]:
    suffix = uuid4().hex[:12]
    return {
        "email": f"dep-{suffix}@example.com",
        "password": "Password123!",
        "full_name": "Dependency User",
    }


def _signup_and_token(client: TestClient) -> tuple[str, UUID]:
    payload = _new_user_payload()
    response = client.post("/auth/signup", json=payload)
    assert response.status_code == 201
    data = response.json()
    return data["access_token"], UUID(data["user"]["id"])


def test_get_current_user_returns_user_model(client: TestClient) -> None:
    token, user_id = _signup_and_token(client)

    with SessionLocal() as db:
        current_user = get_current_user(token=token, db=db)

    assert isinstance(current_user, User)
    assert current_user.id == user_id


def test_get_current_user_id_returns_uuid(client: TestClient) -> None:
    token, user_id = _signup_and_token(client)

    with SessionLocal() as db:
        current_user = get_current_user(token=token, db=db)

    current_user_id = get_current_user_id(current_user)
    assert isinstance(current_user_id, UUID)
    assert current_user_id == user_id


def test_analytics_repository_rejects_user_object_input(client: TestClient) -> None:
    token, _ = _signup_and_token(client)

    with SessionLocal() as db:
        current_user = get_current_user(token=token, db=db)
        with pytest.raises(TypeError, match="UUID scalar"):
            repository.get_total_study_minutes(db, current_user)


def test_analytics_service_rejects_user_object_input(client: TestClient) -> None:
    token, _ = _signup_and_token(client)

    with SessionLocal() as db:
        current_user = get_current_user(token=token, db=db)
        with pytest.raises(TypeError, match="UUID scalar"):
            service.get_dashboard_summary(db, current_user)


def test_event_repository_rejects_non_uuid_identifier_values(client: TestClient) -> None:
    token, _ = _signup_and_token(client)

    with SessionLocal() as db:
        current_user = get_current_user(token=token, db=db)

        class _BadEventPayload:
            def model_dump(self) -> dict[str, object]:
                return {
                    "user_id": current_user,
                    "event_type": "TASK_CREATED",
                    "entity_type": "task",
                    "entity_id": uuid4(),
                    "subject_id": None,
                    "task_id": None,
                    "study_session_id": None,
                    "pomodoro_session_id": None,
                    "note_id": None,
                    "metadata": {},
                }

        with pytest.raises(TypeError, match="UUID or None"):
            events_repository.create_event(db, _BadEventPayload())  # type: ignore[arg-type]
