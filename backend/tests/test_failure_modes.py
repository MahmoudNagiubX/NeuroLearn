from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import ProgrammingError

from app.main import app


BACKEND_ROOT = Path(__file__).resolve().parents[1]
CHECK_DB_SCRIPT = BACKEND_ROOT / "scripts" / "check_db.py"


def _run_check_db(*, env_updates: dict[str, str]) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.update(env_updates)
    return subprocess.run(
        [sys.executable, str(CHECK_DB_SCRIPT)],
        cwd=BACKEND_ROOT,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


def _docker(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["docker", *args],
        cwd=BACKEND_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def _wait_for_db(timeout_seconds: int = 30) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        result = subprocess.run(
            [sys.executable, str(CHECK_DB_SCRIPT)],
            cwd=BACKEND_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return True
        time.sleep(1)
    return False


def test_check_db_fails_with_invalid_password() -> None:
    result = _run_check_db(env_updates={"DATABASE_URL": "", "DB_PASSWORD": "wrong-password"})

    assert result.returncode != 0
    combined_output = (result.stdout + result.stderr).lower()
    assert "database connection failed" in combined_output


def test_check_db_fails_when_all_db_env_vars_missing() -> None:
    result = _run_check_db(
        env_updates={
            "DATABASE_URL": "",
            "DB_HOST": "",
            "DB_PORT": "",
            "DB_NAME": "",
            "DB_USER": "",
            "DB_PASSWORD": "",
        }
    )

    assert result.returncode != 0
    combined_output = (result.stdout + result.stderr).lower()
    assert "database configuration is incomplete" in combined_output or "validationerror" in combined_output


def test_check_db_fails_when_single_db_env_var_missing() -> None:
    result = _run_check_db(env_updates={"DATABASE_URL": "", "DB_USER": ""})

    assert result.returncode != 0
    combined_output = (result.stdout + result.stderr).lower()
    assert "missing" in combined_output


def test_sqlalchemy_programming_error_returns_controlled_payload(client: TestClient, monkeypatch) -> None:
    email = f"schema-{uuid.uuid4().hex[:12]}@example.com"
    signup = client.post(
        "/auth/signup",
        json={"email": email, "password": "Password123!", "full_name": "Schema Failure User"},
    )
    assert signup.status_code == 201
    token = signup.json()["access_token"]

    from app.modules.analytics.service import service as analytics_service

    def _raise_schema_error(*args, **kwargs):
        raise ProgrammingError("SELECT 1", {}, Exception("undefined_column"))

    monkeypatch.setattr(analytics_service, "get_dashboard_summary", _raise_schema_error)

    response = client.get("/analytics/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 500
    assert response.json()["detail"] == "Database schema mismatch detected. Apply latest migrations."


@pytest.mark.integration
def test_login_returns_503_when_database_is_unavailable() -> None:
    ps_result = _docker("ps", "--format", "{{.Names}}")
    if ps_result.returncode != 0:
        pytest.skip(f"Docker is unavailable: {ps_result.stderr.strip()}")

    container_name = "neurolearn-postgres"
    if container_name not in ps_result.stdout:
        pytest.skip("neurolearn-postgres container is not running")

    with TestClient(app) as client:
        stop_result = _docker("stop", container_name)
        if stop_result.returncode != 0:
            pytest.skip(f"Could not stop DB container: {stop_result.stderr.strip()}")

        try:
            response = client.post(
                "/auth/login",
                json={"email": "any@example.com", "password": "any-password"},
            )
            assert response.status_code == 503
            assert response.json()["detail"] == "Database is unavailable. Please try again later."
        finally:
            start_result = _docker("start", container_name)
            if start_result.returncode != 0:
                pytest.fail(f"Failed to restart DB container: {start_result.stderr.strip()}")
            assert _wait_for_db(), "Database did not become healthy after restart"
