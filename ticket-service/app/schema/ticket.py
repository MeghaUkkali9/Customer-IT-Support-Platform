from enum import Enum
from pydantic import BaseModel, Field

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class CreateTicketRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(max_length=5000)
    priority: Priority = Priority.MEDIUM

class UpdateTicketRequest(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    priority: Priority | None = None

class TicketResponse(BaseModel):
    id: str
    title: str
    description: str
    priority: Priority
