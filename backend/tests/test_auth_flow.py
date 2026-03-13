from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient


def _new_user_payload() -> dict[str, str]:
    suffix = uuid4().hex[:12]
    return {
        "email": f"integration-{suffix}@example.com",
        "password": "Password123!",
        "full_name": "Integration User",
    }


def test_signup_creates_user_and_returns_jwt(client: TestClient) -> None:
    payload = _new_user_payload()

    response = client.post("/auth/signup", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)
    assert data["access_token"]
    assert data["user"]["email"] == payload["email"].lower()


def test_login_success_returns_jwt(client: TestClient) -> None:
    payload = _new_user_payload()
    signup = client.post("/auth/signup", json=payload)
    assert signup.status_code == 201

    response = client.post(
        "/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == payload["email"].lower()
    assert data["access_token"]


def test_login_wrong_password_returns_401(client: TestClient) -> None:
    payload = _new_user_payload()
    signup = client.post("/auth/signup", json=payload)
    assert signup.status_code == 201

    response = client.post(
        "/auth/login",
        json={"email": payload["email"], "password": "WrongPassword123!"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password."


def test_login_nonexistent_user_returns_401(client: TestClient) -> None:
    response = client.post(
        "/auth/login",
        json={"email": f"missing-{uuid4().hex[:10]}@example.com", "password": "Password123!"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password."


def test_protected_route_access_with_valid_token(client: TestClient) -> None:
    payload = _new_user_payload()
    signup = client.post("/auth/signup", json=payload)
    assert signup.status_code == 201

    token = signup.json()["access_token"]
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["email"] == payload["email"].lower()
