from __future__ import annotations

from gen_m.models.user import UserRole
from tests.utils import auth_headers


def test_create_ticket(client, make_user, department):
    user, password = make_user("employee1@example.com", role=UserRole.EMPLOYEE)
    headers = auth_headers(client, user.email, password)

    response = client.post(
        "/api/v1/tickets",
        headers=headers,
        json={
            "title": "Printer jam",
            "description": "Paper stuck in tray 2",
            "category": "hardware",
            "department_id": department.id,
            "priority": "low",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["requester_id"] == user.id
    assert body["status"] == "open"


def test_create_ticket_unknown_department(client, make_user):
    user, password = make_user("employee2@example.com")
    headers = auth_headers(client, user.email, password)

    response = client.post(
        "/api/v1/tickets",
        headers=headers,
        json={
            "title": "X",
            "description": "Y",
            "category": "hardware",
            "department_id": 99999,
        },
    )
    assert response.status_code == 404


def test_employee_only_sees_own_tickets(client, make_user, department):
    owner, owner_pw = make_user("owner@example.com")
    other, other_pw = make_user("other@example.com")

    owner_headers = auth_headers(client, owner.email, owner_pw)
    client.post(
        "/api/v1/tickets",
        headers=owner_headers,
        json={
            "title": "Owner's ticket",
            "description": "desc",
            "category": "hardware",
            "department_id": department.id,
        },
    )

    other_headers = auth_headers(client, other.email, other_pw)
    response = client.get("/api/v1/tickets", headers=other_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_employee_cannot_change_status(client, make_user, department):
    user, password = make_user("employee3@example.com")
    headers = auth_headers(client, user.email, password)

    create = client.post(
        "/api/v1/tickets",
        headers=headers,
        json={
            "title": "Ticket",
            "description": "desc",
            "category": "hardware",
            "department_id": department.id,
        },
    )
    ticket_id = create.json()["id"]

    response = client.patch(
        f"/api/v1/tickets/{ticket_id}",
        headers=headers,
        json={"status": "resolved"},
    )
    assert response.status_code == 403


def test_agent_can_resolve_ticket(client, make_user, department):
    employee, employee_pw = make_user("employee4@example.com", department_id=department.id)
    agent, agent_pw = make_user(
        "agent1@example.com", role=UserRole.IT_AGENT, department_id=department.id
    )

    employee_headers = auth_headers(client, employee.email, employee_pw)
    create = client.post(
        "/api/v1/tickets",
        headers=employee_headers,
        json={
            "title": "Broken monitor",
            "description": "desc",
            "category": "hardware",
            "department_id": department.id,
        },
    )
    ticket_id = create.json()["id"]

    agent_headers = auth_headers(client, agent.email, agent_pw)
    response = client.patch(
        f"/api/v1/tickets/{ticket_id}",
        headers=agent_headers,
        json={"status": "resolved"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "resolved"
    assert body["resolved_at"] is not None


def test_ticket_message_thread(client, make_user, department):
    user, password = make_user("employee5@example.com")
    headers = auth_headers(client, user.email, password)

    create = client.post(
        "/api/v1/tickets",
        headers=headers,
        json={
            "title": "Need help",
            "description": "desc",
            "category": "software",
            "department_id": department.id,
        },
    )
    ticket_id = create.json()["id"]

    post_msg = client.post(
        f"/api/v1/tickets/{ticket_id}/messages",
        headers=headers,
        json={"message": "Any update?"},
    )
    assert post_msg.status_code == 201

    list_msgs = client.get(f"/api/v1/tickets/{ticket_id}/messages", headers=headers)
    assert list_msgs.status_code == 200
    messages = list_msgs.json()
    assert len(messages) == 1
    assert messages[0]["message"] == "Any update?"
