from sqlalchemy.orm import Session

from app.models import Profile

PROFILES = [
    {"name": "Dueño", "description": "Dueño del negocio. Acceso total."},
    {"name": "Administrador", "description": "Gestión diaria. Sin configuración crítica."},
    {"name": "Empleado", "description": "Acceso limitado a solicitudes y consultas."},
]


def seed_profiles(db: Session) -> int:
    """Crea los perfiles iniciales."""
    count = 0
    for data in PROFILES:
        existing = db.query(Profile).filter(Profile.name == data["name"]).first()
        if not existing:
            db.add(Profile(**data))
            count += 1
    db.commit()
    return count