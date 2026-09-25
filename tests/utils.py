from __future__ import annotations

from fastapi.testclient import TestClient


def login(client: TestClient, email: str, password: str) -> str:
    response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def auth_headers(client: TestClient, email: str, password: str) -> dict[str, str]:
    token = login(client, email, password)
    return {"Authorization": f"Bearer {token}"}
