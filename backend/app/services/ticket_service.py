from datetime import datetime

from sqlalchemy.orm import Session

from app.models.ticket import Ticket, TicketStatus
from app.repositories.ticket_repository import TicketRepository
from app.schemas.ticket import TicketCreate

class TicketService:
    @staticmethod
    def generate_ticket_number() -> str:
        current_time = datetime.now()
        return current_time.strftime("TCK-%d%m%Y-%H%M%S-%f")

    @staticmethod
    def create_ticket(
        database: Session,
        ticket_data: TicketCreate,
    ) -> Ticket:
        ticket = Ticket(
            ticket_number=TicketService.generate_ticket_number(),
            requester_name=ticket_data.requester_name,
            subject=ticket_data.subject,
            description=ticket_data.description,
            priority=ticket_data.priority,
            status=TicketStatus.open,
        )

        try:
            created_ticket = TicketRepository.create(
                database,
                ticket,
            )
            database.commit()
            database.refresh(created_ticket)
            return created_ticket
        except Exception:
            database.rollback()
            raise

    @staticmethod
    def list_tickets(
        database: Session,
        page: int,
        page_size: int,
    ) -> list[Ticket]:
        offset = (page - 1) * page_size
        return TicketRepository.get_all(
            database,
            offset=offset,
            limit=page_size,
        )
        