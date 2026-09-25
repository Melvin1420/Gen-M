from __future__ import annotations

from gen_m.models.user import UserRole
from tests.utils import auth_headers


def test_non_admin_cannot_create_department(client, make_user):
    user, password = make_user("emp1@example.com")
    headers = auth_headers(client, user.email, password)

    response = client.post(
        "/api/v1/departments", headers=headers, json={"name": "Networking"}
    )
    assert response.status_code == 403


def test_admin_can_create_department(client, make_user):
    admin, password = make_user("admin1@example.com", role=UserRole.ADMIN)
    headers = auth_headers(client, admin.email, password)

    response = client.post(
        "/api/v1/departments", headers=headers, json={"name": "Networking"}
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Networking"


def test_duplicate_department_name_rejected(client, make_user, department):
    admin, password = make_user("admin2@example.com", role=UserRole.ADMIN)
    headers = auth_headers(client, admin.email, password)

    response = client.post(
        "/api/v1/departments", headers=headers, json={"name": department.name}
    )
    assert response.status_code == 400


def test_any_active_user_can_list_and_get_departments(client, make_user, department):
    user, password = make_user("emp2@example.com")
    headers = auth_headers(client, user.email, password)

    list_resp = client.get("/api/v1/departments", headers=headers)
    assert list_resp.status_code == 200
    assert any(d["id"] == department.id for d in list_resp.json())

    get_resp = client.get(f"/api/v1/departments/{department.id}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == department.name


def test_admin_can_rename_department(client, make_user, department):
    admin, password = make_user("admin3@example.com", role=UserRole.ADMIN)
    headers = auth_headers(client, admin.email, password)

    response = client.patch(
        f"/api/v1/departments/{department.id}",
        headers=headers,
        json={"name": "Renamed Department"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Renamed Department"
