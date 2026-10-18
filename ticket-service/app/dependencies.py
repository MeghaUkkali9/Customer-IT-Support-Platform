from app.services.ticket_service import TicketService
from app.repositories.ticket_repository import TicketRepository

def get_database():
    return get_db()

def get_db_repo():
    return TicketRepository()

def get_ticket_service():
    return TicketService()