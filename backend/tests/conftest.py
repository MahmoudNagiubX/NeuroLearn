from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app


BACKEND_ROOT = Path(__file__).resolve().parents[1]


def _run_backend_command(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=BACKEND_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.fixture(scope="session", autouse=True)
def ensure_database_schema() -> None:
    result = _run_backend_command("scripts/apply_migrations.py")
    if result.returncode != 0:
        pytest.fail(
            "Failed to apply migrations before tests.\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )


@pytest.fixture()
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client
