"""Base para modelos que viven en el schema del tenant.

IMPORTANTE: no se define `schema=` explícito. SQLAlchemy resuelve
la tabla usando el `search_path` activo en la sesión.

El `search_path` lo aplica `get_current_tenant` antes de ejecutar
la query del endpoint.
"""

from app.models.base import Base


class TenantBase(Base):
    """Base abstracta para todos los modelos operativos (por-tenant).

    Ejemplo de uso:

        class Resource(TenantBase):
            __tablename__ = "resources"
            ...
    """

    __abstract__ = True