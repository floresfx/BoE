"""Seed de verticales."""

from sqlalchemy.orm import Session

from app.models import Vertical


VERTICALS = [
    {"code": "clinicas_generales", "name": "Clínicas generales", "description": "Clínicas médicas generales"},
    {"code": "clinicas_dentales", "name": "Clínicas dentales", "description": "Consultorios odontológicos"},
    {"code": "panaderias", "name": "Panaderías", "description": "Panaderías y pastelerías"},
    {"code": "restaurantes", "name": "Restaurantes", "description": "Restaurantes y servicios de comida"},
    {"code": "fabricantes", "name": "Fabricantes", "description": "Empresas de manufactura"},
    {"code": "instituciones_educativas", "name": "Instituciones educativas", "description": "Colegios, universidades, centros regulares"},
    {"code": "proyectos_por_encargo", "name": "Proyectos por encargo", "description": "Empresas de proyectos y eventos"},
    {"code": "empresas_limpieza", "name": "Empresas de limpieza", "description": "Servicios de limpieza"},
    {"code": "empresas_mantenimiento", "name": "Empresas de mantenimiento", "description": "Servicios de mantenimiento"},
    {"code": "empresas_transporte", "name": "Empresas de transporte", "description": "Servicios de transporte y logística"},
    {"code": "hoteles", "name": "Hoteles", "description": "Hoteles y hospedaje comercial"},
    {"code": "heladerias", "name": "Heladerías", "description": "Heladerías y sorbeterías"},
    {"code": "talleres", "name": "Talleres", "description": "Talleres mecánicos y de servicios"},
    {"code": "ferreterias", "name": "Ferreterías", "description": "Ferreterías y materiales"},
    {"code": "distribuidoras", "name": "Distribuidoras", "description": "Distribuidoras mayoristas"},
    {"code": "laboratorios", "name": "Laboratorios", "description": "Laboratorios clínicos y de análisis"},
    {"code": "academias", "name": "Academias", "description": "Academias y centros de formación corta"},
    {"code": "construccion", "name": "Construcción", "description": "Empresas de construcción"},
    {"code": "diseño", "name": "Diseño", "description": "Estudios de diseño y creatividad"},
]


def seed_verticals(db: Session) -> int:
    """Crea los verticales iniciales. Idempotente."""
    count = 0
    for data in VERTICALS:
        existing = (
            db.query(Vertical).filter(Vertical.code == data["code"]).first()
        )
        if not existing:
            db.add(Vertical(**data))
            count += 1
    db.commit()
    return count