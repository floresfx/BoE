from sqlalchemy.orm import Session

from app.models import Role

ROLES = [
    {
        "name": "SuperAdmin",
        "description": "Administrador del SaaS. Acceso total al panel de administración.",
        "is_system": True,
    },
    {
        "name": "Admin",
        "description": "Control total del tenant",
        "is_system": True,
    },
    {
        "name": "Editor",
        "description": "Crear y modificar",
        "is_system": True,
    },
    {
        "name": "Lector",
        "description": "Solo visualización",
        "is_system": True,
    },
]


def seed_roles(db: Session) -> int:
    """Crea los roles del sistema. Globales, sin tenant_id."""
    count = 0
    for data in ROLES:
        existing = db.query(Role).filter(Role.name == data["name"]).first()
        if not existing:
            db.add(Role(**data))
            count += 1
    db.commit()
    return count