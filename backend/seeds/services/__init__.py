"""Seeds de servicios."""

from seeds.services.service_templates import seed_service_templates
from seeds.services.verticals_services import seed_verticals_services

__all__ = [
    "seed_service_templates",
    "seed_verticals_services",
]