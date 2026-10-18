import hashlib
from typing import Optional

from app.exceptions.ticket_exception import IdempotencyKeyReusedException, TicketNotFoundException
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

    async def create(self, payload: CreateTicketRequest, idempotency_key: Optional[str] = None) -> Ticket:
        if idempotency_key is None:
            return await self._create_ticket(payload)

        request_hash = hashlib.sha256(payload.model_dump_json().encode()).hexdigest()

        if await self.db_repo.claim_idempotency_key(idempotency_key, request_hash):
            ticket = await self._create_ticket(payload)
            await self.db_repo.set_idempotency_ticket(idempotency_key, ticket.id)
            return ticket

        # Key seen before: replay the original result instead of creating a duplicate
        record = await self.db_repo.get_idempotency_key(idempotency_key)
        if record.request_hash != request_hash:
            raise IdempotencyKeyReusedException(idempotency_key)
        if record.ticket_id is None:
            raise TicketNotFoundException(idempotency_key)  # original ticket was deleted
        return await self.get(record.ticket_id)

    async def _create_ticket(self, payload: CreateTicketRequest) -> Ticket:
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
