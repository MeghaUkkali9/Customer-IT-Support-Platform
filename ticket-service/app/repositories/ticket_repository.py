from app.models.ticket_model import Ticket
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

class TicketRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def list(self, limit: int, offset:int)-> list[Ticket]:
        result = await self.db.execute(
            select(Ticket).order_by(Ticket.created_at.desc()).limit(limit).offset(offset)
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