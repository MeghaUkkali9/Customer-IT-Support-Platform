from app.models.idempotency_model import IdempotencyKey
from app.models.ticket_model import Ticket
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

class TicketRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def list(self, limit: int, offset:int, created_by: Optional[str] = None)-> list[Ticket]:
        query = select(Ticket)
        if created_by is not None:
            query = query.where(Ticket.created_by == created_by)
        result = await self.db.execute(
            query.order_by(Ticket.created_at.desc()).limit(limit).offset(offset)
        )
        
        return list(result.scalars().all())
    
    async def get(self, ticket_id: str) -> Optional[Ticket]:
        return await self.db.get(Ticket, ticket_id)
    
    async def create(self, ticket: Ticket) -> Ticket:
        self.db.add(ticket)
        
        await self.db.flush()
        await self.db.refresh(ticket)
        
        return ticket
    
    async def update(self, ticket: Ticket, fields: dict) -> Ticket:
        for key, value in fields.items():
            setattr(ticket, key, value)
            
        await self.db.flush()
        await self.db.refresh(ticket)
        return ticket
    
    async def delete(self, ticket: Ticket) -> None:
        await self.db.delete(ticket)
        await self.db.flush()

    async def claim_idempotency_key(self, key: str, request_hash: str) -> bool:
        # Returns True if this request claimed the key, False if it already existed.
        # If another transaction holds the same key uncommitted, Postgres makes this
        # INSERT wait until that transaction finishes, so concurrent duplicates are safe.
        result = await self.db.execute(
            insert(IdempotencyKey)
            .values(key=key, request_hash=request_hash)
            .on_conflict_do_nothing(index_elements=[IdempotencyKey.key])
            .returning(IdempotencyKey.key)
        )
        return result.scalar_one_or_none() is not None

    async def get_idempotency_key(self, key: str) -> Optional[IdempotencyKey]:
        return await self.db.get(IdempotencyKey, key)

    async def set_idempotency_ticket(self, key: str, ticket_id: str) -> None:
        record = await self.db.get(IdempotencyKey, key)
        record.ticket_id = ticket_id
        await self.db.flush()