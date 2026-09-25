from __future__ import annotations

from gen_m.models.user import UserRole
from tests.utils import auth_headers, login


def test_non_admin_cannot_access_users(client, make_user):
    user, password = make_user("emp3@example.com")
    headers = auth_headers(client, user.email, password)

    response = client.get("/api/v1/users", headers=headers)
    assert response.status_code == 403


def test_admin_can_create_user(client, make_user, department):
    admin, admin_pw = make_user("admin4@example.com", role=UserRole.ADMIN)
    headers = auth_headers(client, admin.email, admin_pw)

    response = client.post(
        "/api/v1/users",
        headers=headers,
        json={
            "email": "newagent@example.com",
            "full_name": "New Agent",
            "password": "AgentPass123!",
            "role": "it_agent",
            "department_id": department.id,
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "newagent@example.com"
    assert body["role"] == "it_agent"
    assert "password" not in body
    assert "hashed_password" not in body

    # the created account can actually log in with the password the admin set
    token = login(client, "newagent@example.com", "AgentPass123!")
    assert token


def test_duplicate_email_rejected(client, make_user):
    admin, admin_pw = make_user("admin5@example.com", role=UserRole.ADMIN)
    existing, _ = make_user("taken@example.com")
    headers = auth_headers(client, admin.email, admin_pw)

    response = client.post(
        "/api/v1/users",
        headers=headers,
        json={
            "email": existing.email,
            "full_name": "Someone",
            "password": "Whatever123!",
        },
    )
    assert response.status_code == 400


def test_admin_can_list_and_get_users(client, make_user):
    admin, admin_pw = make_user("admin6@example.com", role=UserRole.ADMIN)
    other, _ = make_user("visible@example.com")
    headers = auth_headers(client, admin.email, admin_pw)

    list_resp = client.get("/api/v1/users", headers=headers)
    assert list_resp.status_code == 200
    assert any(u["id"] == other.id for u in list_resp.json())

    get_resp = client.get(f"/api/v1/users/{other.id}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["email"] == other.email


def test_admin_can_update_role_and_deactivate_other_user(client, make_user):
    admin, admin_pw = make_user("admin7@example.com", role=UserRole.ADMIN)
    other, _ = make_user("tobemodified@example.com")
    headers = auth_headers(client, admin.email, admin_pw)

    response = client.patch(
        f"/api/v1/users/{other.id}",
        headers=headers,
        json={"role": "manager", "is_active": False},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["role"] == "manager"
    assert body["is_active"] is False


def test_admin_cannot_deactivate_self(client, make_user):
    admin, admin_pw = make_user("admin8@example.com", role=UserRole.ADMIN)
    headers = auth_headers(client, admin.email, admin_pw)

    response = client.patch(
        f"/api/v1/users/{admin.id}", headers=headers, json={"is_active": False}
    )
    assert response.status_code == 400


def test_admin_cannot_remove_own_admin_role(client, make_user):
    admin, admin_pw = make_user("admin9@example.com", role=UserRole.ADMIN)
    headers = auth_headers(client, admin.email, admin_pw)

    response = client.patch(
        f"/api/v1/users/{admin.id}", headers=headers, json={"role": "employee"}
    )
    assert response.status_code == 400


def test_admin_can_reset_another_users_password(client, make_user):
    admin, admin_pw = make_user("admin10@example.com", role=UserRole.ADMIN)
    other, other_pw = make_user("resetme@example.com")
    headers = auth_headers(client, admin.email, admin_pw)

    response = client.patch(
        f"/api/v1/users/{other.id}", headers=headers, json={"password": "NewPass123!"}
    )
    assert response.status_code == 200

    # old password no longer works, new one does
    bad_login = client.post(
        "/api/v1/auth/login", data={"username": other.email, "password": other_pw}
    )
    assert bad_login.status_code == 401

    new_token = login(client, other.email, "NewPass123!")
    assert new_token
