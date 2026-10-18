from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query, status

from app.core.security import CurrentUser, get_current_user, require_agent
from app.dependencies import get_ticket_service
from app.schema.ticket import CreateTicketRequest, UpdateTicketRequest, TicketResponse
from app.services.ticket_service import TicketService

# Every route below requires a valid token
router = APIRouter(prefix="/api/v1/tickets", tags=["tickets"])

@router.get("", response_model=list[TicketResponse])
async def list_tickets(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: CurrentUser = Depends(get_current_user),
    service: TicketService = Depends(get_ticket_service),
):
    return await service.list(limit=limit, offset=offset, user=user)

@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: UUID,
    user: CurrentUser = Depends(get_current_user),
    service: TicketService = Depends(get_ticket_service),
):
    return await service.get(str(ticket_id), user)


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    payload: CreateTicketRequest,
    idempotency_key: str | None = Header(None, min_length=1, max_length=200),  # "Idempotency-Key" header
    user: CurrentUser = Depends(get_current_user),
    service: TicketService = Depends(get_ticket_service),
):
    return await service.create(payload, user, idempotency_key)


@router.patch("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: UUID,
    payload: UpdateTicketRequest,
    user: CurrentUser = Depends(get_current_user),
    service: TicketService = Depends(get_ticket_service),
):
    return await service.update(str(ticket_id), payload, user)


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ticket(
    ticket_id: UUID,
    user: CurrentUser = Depends(require_agent),  # agents only
    service: TicketService = Depends(get_ticket_service),
):
    await service.delete(str(ticket_id), user)
