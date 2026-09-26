from __future__ import annotations

from gen_m.models.user import UserRole
from tests.utils import auth_headers


def test_non_staff_cannot_create_asset(client, make_user):
    user, password = make_user("employee1@example.com")
    headers = auth_headers(client, user.email, password)

    response = client.post(
        "/api/v1/assets",
        headers=headers,
        json={"asset_tag": "LT-001", "name": "Dell Laptop", "category": "laptop"},
    )
    assert response.status_code == 403


def test_agent_can_create_asset(client, make_user):
    agent, password = make_user("agent1@example.com", role=UserRole.IT_AGENT)
    headers = auth_headers(client, agent.email, password)

    response = client.post(
        "/api/v1/assets",
        headers=headers,
        json={"asset_tag": "LT-001", "name": "Dell Laptop", "category": "laptop"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["asset_tag"] == "LT-001"
    assert body["status"] == "in_storage"


def test_duplicate_asset_tag_rejected(client, make_user):
    admin, password = make_user("admin1@example.com", role=UserRole.ADMIN)
    headers = auth_headers(client, admin.email, password)

    client.post(
        "/api/v1/assets",
        headers=headers,
        json={"asset_tag": "LT-002", "name": "HP Laptop", "category": "laptop"},
    )
    response = client.post(
        "/api/v1/assets",
        headers=headers,
        json={"asset_tag": "LT-002", "name": "Another Laptop", "category": "laptop"},
    )
    assert response.status_code == 400


def test_create_asset_unknown_assigned_user(client, make_user):
    admin, password = make_user("admin2@example.com", role=UserRole.ADMIN)
    headers = auth_headers(client, admin.email, password)

    response = client.post(
        "/api/v1/assets",
        headers=headers,
        json={
            "asset_tag": "LT-003",
            "name": "Laptop",
            "category": "laptop",
            "assigned_to_id": 99999,
        },
    )
    assert response.status_code == 404


def test_employee_sees_only_assigned_assets(client, make_user):
    admin, admin_pw = make_user("admin3@example.com", role=UserRole.ADMIN)
    employee, employee_pw = make_user("employee2@example.com")
    other_employee, other_pw = make_user("employee3@example.com")

    admin_headers = auth_headers(client, admin.email, admin_pw)
    create = client.post(
        "/api/v1/assets",
        headers=admin_headers,
        json={
            "asset_tag": "LT-004",
            "name": "Laptop",
            "category": "laptop",
            "assigned_to_id": employee.id,
        },
    )
    assert create.status_code == 201

    employee_headers = auth_headers(client, employee.email, employee_pw)
    my_assets = client.get("/api/v1/assets", headers=employee_headers)
    assert my_assets.status_code == 200
    assert len(my_assets.json()) == 1
    assert my_assets.json()[0]["asset_tag"] == "LT-004"

    other_headers = auth_headers(client, other_employee.email, other_pw)
    other_assets = client.get("/api/v1/assets", headers=other_headers)
    assert other_assets.status_code == 200
    assert other_assets.json() == []


def test_manager_sees_department_assets(client, make_user, department):
    admin, admin_pw = make_user("admin4@example.com", role=UserRole.ADMIN)
    manager, manager_pw = make_user(
        "manager1@example.com", role=UserRole.MANAGER, department_id=department.id
    )

    admin_headers = auth_headers(client, admin.email, admin_pw)
    client.post(
        "/api/v1/assets",
        headers=admin_headers,
        json={
            "asset_tag": "LT-005",
            "name": "Laptop",
            "category": "laptop",
            "department_id": department.id,
        },
    )

    manager_headers = auth_headers(client, manager.email, manager_pw)
    response = client.get("/api/v1/assets", headers=manager_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["asset_tag"] == "LT-005"


def test_agent_can_update_asset_status(client, make_user):
    agent, password = make_user("agent2@example.com", role=UserRole.IT_AGENT)
    headers = auth_headers(client, agent.email, password)

    create = client.post(
        "/api/v1/assets",
        headers=headers,
        json={"asset_tag": "LT-006", "name": "Laptop", "category": "laptop"},
    )
    asset_id = create.json()["id"]

    response = client.patch(
        f"/api/v1/assets/{asset_id}",
        headers=headers,
        json={"status": "under_repair"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "under_repair"


def test_employee_cannot_update_asset(client, make_user):
    admin, admin_pw = make_user("admin5@example.com", role=UserRole.ADMIN)
    employee, employee_pw = make_user("employee4@example.com")

    admin_headers = auth_headers(client, admin.email, admin_pw)
    create = client.post(
        "/api/v1/assets",
        headers=admin_headers,
        json={"asset_tag": "LT-007", "name": "Laptop", "category": "laptop"},
    )
    asset_id = create.json()["id"]

    employee_headers = auth_headers(client, employee.email, employee_pw)
    response = client.patch(
        f"/api/v1/assets/{asset_id}",
        headers=employee_headers,
        json={"status": "retired"},
    )
    assert response.status_code == 403
