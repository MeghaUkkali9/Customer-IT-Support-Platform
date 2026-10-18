from typing import Optional
from app.schema.ticket import CreateTicketRequest, UpdateTicketRequest, TicketResponse

class TicketService:
    def __init__(self, db_repo):
        self.db_repo = db_repo
        
    def list(limit: Optional[int], offset: Optional[int]):
        pass
    
    def get(ticket_id: str):
        pass
    
    def create(payload: CreateTicketRequest):
        pass
    
    def update(ticket_id: str, payload: UpdateTicketRequest):
        pass
    
    def delete(ticket_id: str):
        pass