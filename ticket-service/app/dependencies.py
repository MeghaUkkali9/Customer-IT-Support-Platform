from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.datbase import get_db
from app.services.ticket_service import TicketService
from app.repositories.ticket_repository import TicketRepository

def get_db_repo(db: AsyncSession = Depends(get_db)) -> TicketRepository:
    return TicketRepository(db)

def get_ticket_service(db_repo: TicketRepository = Depends(get_db_repo))-> TicketService:
    return TicketService(db_repo)