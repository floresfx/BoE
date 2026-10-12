from sqlalchemy.orm import Session

from app.models import Vertical

VERTICALS = [
    {"name": "Clínicas generales", "description": "Clínicas médicas generales"},
    {"name": "Clínicas dentales", "description": "Consultorios odontológicos"},
    {"name": "Panaderías", "description": "Panaderías y pastelerías"},
    {"name": "Restaurantes", "description": "Restaurantes y servicios de comida"},
    {"name": "Fabricantes", "description": "Empresas de manufactura"},
    {"name": "Instituciones educativas", "description": "Colegios, academias, universidades"},
    {"name": "Proyectos por encargo", "description": "Empresas de proyectos y eventos"},
    {"name": "Empresas de limpieza", "description": "Servicios de limpieza"},
    {"name": "Empresas de mantenimiento", "description": "Servicios de mantenimiento"},
    {"name": "Empresas de transporte", "description": "Servicios de transporte y logística"},
]


def seed_verticals(db: Session) -> int:
    """Crea los verticales iniciales."""
    count = 0
    for data in VERTICALS:
        existing = db.query(Vertical).filter(Vertical.name == data["name"]).first()
        if not existing:
            db.add(Vertical(**data))
            count += 1
    db.commit()
    return count