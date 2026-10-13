"""Seed de feature flags."""

from sqlalchemy.orm import Session

from app.models import Feature


FEATURES = [
    {"code": "inventario", "name": "Inventario", "description": "Gestion de inventario", "applies_to": "mpr"},
    {"code": "planificacion", "name": "Planificacion", "description": "Calendario + Kanban", "applies_to": "mpr"},
    {"code": "anexos", "name": "Anexos", "description": "Anexos a produccion", "applies_to": "mpr"},
    {"code": "excepciones", "name": "Excepciones", "description": "Manejo de excepciones", "applies_to": "mpr"},
    {"code": "costeo_basico", "name": "Costeo basico", "description": "Calculo de costos basico", "applies_to": "mpr"},
    {"code": "costeo_completo", "name": "Costeo completo", "description": "Costeo avanzado con snapshots", "applies_to": "mpr"},
    {"code": "ia_basica", "name": "IA basica", "description": "Recomendaciones simples", "applies_to": "mpr"},
    {"code": "ia_completa", "name": "IA completa", "description": "Opportunity Engine", "applies_to": "mpr"},
    {"code": "marketplace", "name": "Marketplace", "description": "Acceso al marketplace", "applies_to": "both"},
    {"code": "multi_moneda", "name": "Multi-moneda", "description": "Soporte multi-moneda", "applies_to": "both"},
    {"code": "multi_usuario", "name": "Multi-usuario", "description": "Mas de 1 usuario", "applies_to": "mpr"},
    {"code": "api_access", "name": "API Access", "description": "Acceso programatico", "applies_to": "both"},
    {"code": "exportacion", "name": "Exportacion", "description": "Exportar a CSV/Excel/JSON", "applies_to": "both"},
    {"code": "importacion", "name": "Importacion", "description": "Importar desde Excel", "applies_to": "both"},
    {"code": "notificaciones", "name": "Notificaciones", "description": "Email + push", "applies_to": "both"},
    {"code": "auditoria", "name": "Auditoria", "description": "Logs de cambios", "applies_to": "mpr"},
    {"code": "multi_bodega", "name": "Multi-bodega", "description": "Multiples ubicaciones de inventario", "applies_to": "mpr"},
    {"code": "proveedores", "name": "Proveedores", "description": "Gestion de proveedores", "applies_to": "mpr"},
    {"code": "cotizaciones", "name": "Cotizaciones", "description": "Sistema de cotizaciones", "applies_to": "marketplace"},
    {"code": "insignias", "name": "Insignias", "description": "Sistema de reputacion", "applies_to": "marketplace"},
    {"code": "permisos_normas", "name": "Permisos y normas", "description": "Declaracion de permisos regulatorios", "applies_to": "marketplace"},
    {"code": "asistente_ia", "name": "Asistente IA", "description": "Chatbot conversacional", "applies_to": "both"},
    {"code": "prediccion_demanda", "name": "Prediccion de demanda", "description": "ML para demanda", "applies_to": "mpr"},
    {"code": "prediccion_mermas", "name": "Prediccion de mermas", "description": "ML para mermas", "applies_to": "mpr"},
    {"code": "matching_inverso", "name": "Matching inverso", "description": "Que puedo hacer con lo que tengo", "applies_to": "mpr"},
]


def seed_features(db: Session) -> int:
    """Crea los feature flags iniciales. Idempotente."""
    count = 0
    for data in FEATURES:
        existing = (
            db.query(Feature).filter(Feature.code == data["code"]).first()
        )
        if not existing:
            db.add(Feature(**data))
            count += 1
    db.commit()
    return count