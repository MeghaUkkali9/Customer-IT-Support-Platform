from fastapi import APIRouter, Depends, Query, status

from app.dependencies import get_ticket_service
from app.schema.ticket import CreateTicketRequest, UpdateTicketRequest, TicketResponse
from app.services.ticket_service import TicketService

router = APIRouter(prefix="/api/v1/tickets", tags=["tickets"])

@router.get("", response_model=list[TicketResponse])
async def list_tickets(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: TicketService = Depends(get_ticket_service),
):
    return await service.list(limit=limit, offset=offset)

@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(ticket_id: str, service: TicketService = Depends(get_ticket_service)):
    return await service.get(ticket_id)


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(payload: CreateTicketRequest, service: TicketService = Depends(get_ticket_service)):
    return await service.create(payload)


@router.patch("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(ticket_id: str, payload: UpdateTicketRequest, service: TicketService = Depends(get_ticket_service)):
    return await service.update(ticket_id, payload)


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ticket(ticket_id: str, service: TicketService = Depends(get_ticket_service)):
    await service.delete(ticket_id)
