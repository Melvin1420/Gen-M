from __future__ import annotations

from tests.utils import auth_headers, login


def test_login_success(client, make_user):
    user, password = make_user("agent@example.com")
    token = login(client, user.email, password)
    assert token


def test_login_wrong_password(client, make_user):
    user, _ = make_user("agent2@example.com")
    response = client.post(
        "/api/v1/auth/login",
        data={"username": user.email, "password": "WrongPassword!"},
    )
    assert response.status_code == 401


def test_login_unknown_email(client):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "nobody@example.com", "password": "whatever"},
    )
    assert response.status_code == 401


def test_me_requires_token(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_me_returns_current_user(client, make_user):
    user, password = make_user("me@example.com")
    headers = auth_headers(client, user.email, password)

    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == user.email
    assert body["role"] == user.role.value
