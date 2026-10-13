"""Modelos de servicios."""

from app.models.services.service_template import ServiceTemplate
from app.models.services.vertical_service import VerticalService

__all__ = [
    "ServiceTemplate",
    "VerticalService",
]