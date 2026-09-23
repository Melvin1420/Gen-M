from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import or_, select

from gen_m.api.dependencies import ActiveUser, DatabaseSession
from gen_m.models.department import Department
from gen_m.models.ticket import Ticket, TicketStatus
from gen_m.models.ticket_message import TicketMessage
from gen_m.models.user import User, UserRole
from gen_m.schemas.ticket import (
    TicketCreate,
    TicketMessageCreate,
    TicketMessageRead,
    TicketRead,
    TicketUpdate,
)

router = APIRouter(prefix="/tickets", tags=["tickets"])

STAFF_ROLES = (UserRole.IT_AGENT, UserRole.MANAGER, UserRole.ADMIN)


def _get_ticket_or_404(db: DatabaseSession, ticket_id: int) -> Ticket:
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return ticket


def _can_view(user: User, ticket: Ticket) -> bool:
    if user.role == UserRole.ADMIN:
        return True
    if user.role == UserRole.MANAGER:
        return ticket.department_id == user.department_id
    if user.role == UserRole.IT_AGENT:
        return ticket.assigned_agent_id == user.id or (
            ticket.assigned_agent_id is None and ticket.department_id == user.department_id
        )
    return ticket.requester_id == user.id


@router.post("", response_model=TicketRead, status_code=status.HTTP_201_CREATED)
def create_ticket(payload: TicketCreate, db: DatabaseSession, current_user: ActiveUser) -> Ticket:
    if db.get(Department, payload.department_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")

    ticket = Ticket(
        title=payload.title,
        description=payload.description,
        category=payload.category,
        department_id=payload.department_id,
        priority=payload.priority,
        asset_id=payload.asset_id,
        requester_id=current_user.id,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.get("", response_model=list[TicketRead])
def list_tickets(db: DatabaseSession, current_user: ActiveUser) -> list[Ticket]:
    stmt = select(Ticket)

    if current_user.role == UserRole.ADMIN:
        pass
    elif current_user.role == UserRole.MANAGER:
        stmt = stmt.where(Ticket.department_id == current_user.department_id)
    elif current_user.role == UserRole.IT_AGENT:
        stmt = stmt.where(
            or_(
                Ticket.assigned_agent_id == current_user.id,
                (Ticket.assigned_agent_id.is_(None))
                & (Ticket.department_id == current_user.department_id),
            )
        )
    else:
        stmt = stmt.where(Ticket.requester_id == current_user.id)

    return list(db.execute(stmt.order_by(Ticket.created_at.desc())).scalars())


@router.get("/{ticket_id}", response_model=TicketRead)
def get_ticket(ticket_id: int, db: DatabaseSession, current_user: ActiveUser) -> Ticket:
    ticket = _get_ticket_or_404(db, ticket_id)
    if not _can_view(current_user, ticket):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return ticket


@router.patch("/{ticket_id}", response_model=TicketRead)
def update_ticket(
    ticket_id: int, payload: TicketUpdate, db: DatabaseSession, current_user: ActiveUser
) -> Ticket:
    ticket = _get_ticket_or_404(db, ticket_id)
    if not _can_view(current_user, ticket):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    is_staff = current_user.role in STAFF_ROLES
    data = payload.model_dump(exclude_unset=True)

    if not is_staff:
        if ticket.requester_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
            )
        if ticket.status != TicketStatus.OPEN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ticket can only be edited by the requester while it is open",
            )
        allowed_fields = {"title", "description"}
        if not set(data).issubset(allowed_fields):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Requesters may only edit title and description",
            )

    if "department_id" in data:
        if db.get(Department, data["department_id"]) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Department not found"
            )

    if "assigned_agent_id" in data and data["assigned_agent_id"] is not None:
        if db.get(User, data["assigned_agent_id"]) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    for field, value in data.items():
        setattr(ticket, field, value)

    if "status" in data:
        if data["status"] == TicketStatus.RESOLVED and ticket.resolved_at is None:
            ticket.resolved_at = datetime.now(timezone.utc)
        elif data["status"] in (TicketStatus.OPEN, TicketStatus.IN_PROGRESS):
            ticket.resolved_at = None

    db.commit()
    db.refresh(ticket)
    return ticket


@router.get("/{ticket_id}/messages", response_model=list[TicketMessageRead])
def list_messages(
    ticket_id: int, db: DatabaseSession, current_user: ActiveUser
) -> list[TicketMessage]:
    ticket = _get_ticket_or_404(db, ticket_id)
    if not _can_view(current_user, ticket):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    stmt = (
        select(TicketMessage)
        .where(TicketMessage.ticket_id == ticket_id)
        .order_by(TicketMessage.created_at)
    )
    return list(db.execute(stmt).scalars())


@router.post(
    "/{ticket_id}/messages",
    response_model=TicketMessageRead,
    status_code=status.HTTP_201_CREATED,
)
def create_message(
    ticket_id: int, payload: TicketMessageCreate, db: DatabaseSession, current_user: ActiveUser
) -> TicketMessage:
    ticket = _get_ticket_or_404(db, ticket_id)
    if not _can_view(current_user, ticket):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    message = TicketMessage(
        ticket_id=ticket_id, sender_id=current_user.id, message=payload.message
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message
