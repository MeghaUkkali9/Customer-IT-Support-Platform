import hashlib
from typing import Optional

from app.core.security import CurrentUser
from app.exceptions.ticket_exception import IdempotencyKeyReusedException, TicketNotFoundException
from app.models.ticket_model import Ticket
from app.repositories.ticket_repository import TicketRepository
from app.schema.ticket import CreateTicketRequest, UpdateTicketRequest

class TicketService:
    def __init__(self, db_repo: TicketRepository):
        self.db_repo = db_repo

    async def list(self, limit: int, offset: int, user: CurrentUser) -> list[Ticket]:
        # Agents see every ticket; customers only their own
        created_by = None if user.is_agent else user.id
        return await self.db_repo.list(limit=limit, offset=offset, created_by=created_by)

    async def get(self, ticket_id: str, user: CurrentUser) -> Ticket:
        ticket = await self.db_repo.get(ticket_id=ticket_id)
        
        # Someone else's ticket is reported as "not found" (not 403) so customers
        # can't discover which ticket ids exist
        if ticket is None or (not user.is_agent and ticket.created_by != user.id):
            raise TicketNotFoundException(ticket_id)
        
        return ticket

    async def create(self, payload: CreateTicketRequest, user: CurrentUser, idempotency_key: Optional[str] = None) -> Ticket:
        if idempotency_key is None:
            return await self._create_ticket(payload, user)

        # Scope keys per user so two users picking the same key never collide
        idempotency_key = f"{user.id}:{idempotency_key}"
        request_hash = hashlib.sha256(payload.model_dump_json().encode()).hexdigest()

        if await self.db_repo.claim_idempotency_key(idempotency_key, request_hash):
            ticket = await self._create_ticket(payload, user)
            await self.db_repo.set_idempotency_ticket(idempotency_key, ticket.id)
            return ticket

        # Key seen before: replay the original result instead of creating a duplicate
        record = await self.db_repo.get_idempotency_key(idempotency_key)
        if record.request_hash != request_hash:
            raise IdempotencyKeyReusedException(idempotency_key)
        if record.ticket_id is None:
            raise TicketNotFoundException(record.key.split(":", 1)[1])  # original ticket was deleted
        return await self.get(record.ticket_id, user)

    async def _create_ticket(self, payload: CreateTicketRequest, user: CurrentUser) -> Ticket:
        ticket = Ticket(
            title = payload.title,
            description = payload.description,
            priority = payload.priority.value,
            created_by = user.id
        )
        return await self.db_repo.create(ticket)
    
    async def update(self, ticket_id: str, payload: UpdateTicketRequest, user: CurrentUser) -> Ticket:
        ticket = await self.get(ticket_id, user)
        fields = payload.model_dump(exclude_unset=True, mode="json")
        return await self.db_repo.update(ticket, fields)

    async def delete(self, ticket_id: str, user: CurrentUser) -> None:
        ticket = await self.get(ticket_id=ticket_id, user=user)
        await self.db_repo.delete(ticket)
