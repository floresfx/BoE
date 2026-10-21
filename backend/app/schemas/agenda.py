from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class CalendarEvent(BaseModel):
    """Un evento genérico para el calendario."""
    id: UUID
    title: str
    start: datetime
    end: datetime | None = None
    type: str  # "production_order" | "purchase_request"
    status: str
    color: str


class CalendarResponse(BaseModel):
    events: list[CalendarEvent]