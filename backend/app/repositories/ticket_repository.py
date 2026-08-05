from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ticket import Ticket

class TicketRepository:
    @staticmethod
    def create(database: Session, ticket: Ticket) -> Ticket:
        database.add(ticket)
        return ticket

    @staticmethod
    def get_all(
        database: Session,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Ticket]:
        return (
            database.scalars(
                select(Ticket)
                .order_by(Ticket.ticket_id.desc())
                .offset(offset)
                .limit(limit)
            ).all()
        )
