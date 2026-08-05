from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_database_session
from app.schemas.ticket import TicketCreate, TicketResponse
from app.services.ticket_service import TicketService

router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"],
)

@router.post(
    "",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_ticket(
    ticket_data: TicketCreate,
    database: Session = Depends(get_database_session),
) -> TicketResponse:
    return TicketService.create_ticket(
        database=database,
        ticket_data=ticket_data,
    )

@router.get(
    "",
    response_model=list[TicketResponse],
)
def list_tickets(
    database: Session = Depends(get_database_session),
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[TicketResponse]:
    return TicketService.list_tickets(
        database=database,
        page=page,
        page_size=page_size,
    )

