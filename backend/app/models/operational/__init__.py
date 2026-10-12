"""Modelos operativos (por tenant).

Estos modelos NO viven en `public`. Viven en el schema del tenant,
resuelto dinámicamente vía `search_path`.
"""

from app.models.operational.resource import Resource, RESOURCE_TYPES

__all__ = ["Resource", "RESOURCE_TYPES"]