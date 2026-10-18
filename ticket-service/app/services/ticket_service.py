from app.exceptions.ticket_exception import TicketNotFoundException
from app.models.ticket_model import Ticket
from app.repositories.ticket_repository import TicketRepository
from app.schema.ticket import CreateTicketRequest, UpdateTicketRequest

class TicketService:
    def __init__(self, db_repo: TicketRepository):
        self.db_repo = db_repo

    async def list(self, limit: int, offset: int) -> list[Ticket]:
        return await self.db_repo.list(limit=limit, offset=offset)

    async def get(self, ticket_id: str) -> Ticket:
        ticket = await self.db_repo.get(ticket_id=ticket_id)
        
        if ticket is None:
            raise TicketNotFoundException(ticket_id)
        
        return ticket

    async def create(self, payload: CreateTicketRequest) -> Ticket:
        ticket = Ticket(
            title = payload.title,
            description = payload.description,
            priority = payload.priority.value
        )
        return await self.db_repo.create(ticket)
    
    async def update(self, ticket_id: str, payload: UpdateTicketRequest) -> Ticket:
        ticket = await self.get(ticket_id)
        fields = payload.model_dump(exclude_unset=True, mode="json")
        return await self.db_repo.update(ticket, fields)

    async def delete(self, ticket_id: str) -> None:
        ticket = await self.get(ticket_id=ticket_id)
        await self.db_repo.delete(ticket)
