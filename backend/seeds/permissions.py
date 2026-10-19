from sqlalchemy.orm import Session

from app.models import Permission

PERMISSIONS = [
    # Bundle
    {"module": "bundle", "action": "ver", "description": "Ver paquetes"},
    {"module": "bundle", "action": "crear", "description": "Crear paquetes"},
    {"module": "bundle", "action": "editar", "description": "Editar paquetes"},
    {"module": "bundle", "action": "eliminar", "description": "Eliminar paquetes"},
    {"module": "bundle", "action": "versionar", "description": "Versionar paquetes"},
    {"module": "bundle", "action": "activar", "description": "Activar paquetes"},
    {"module": "bundle", "action": "exportar", "description": "Exportar paquetes"},
    {"module": "bundle", "action": "importar", "description": "Importar paquetes"},

    # Inventory
    {"module": "inventory", "action": "ver", "description": "Ver inventario"},
    {"module": "inventory", "action": "crear", "description": "Crear inventario"},
    {"module": "inventory", "action": "editar", "description": "Editar inventario"},
    {"module": "inventory", "action": "eliminar", "description": "Eliminar inventario"},
    {"module": "inventory", "action": "ajustar", "description": "Ajustar inventario"},
    {"module": "inventory", "action": "transferir", "description": "Transferir inventario"},
    {"module": "inventory", "action": "exportar", "description": "Exportar inventario"},
    {"module": "inventory", "action": "importar", "description": "Importar inventario"},
    {"module": "inventory", "action": "ver_costos", "description": "Ver costos"},
    {"module": "inventory", "action": "ver_lotes", "description": "Ver lotes"},

    # Request
    {"module": "request", "action": "ver", "description": "Ver solicitudes"},
    {"module": "request", "action": "crear", "description": "Crear solicitudes"},
    {"module": "request", "action": "editar", "description": "Editar solicitudes"},
    {"module": "request", "action": "eliminar", "description": "Eliminar solicitudes"},
    {"module": "request", "action": "aprobar", "description": "Aprobar solicitudes"},
    {"module": "request", "action": "rechazar", "description": "Rechazar solicitudes"},
    {"module": "request", "action": "ejecutar", "description": "Ejecutar solicitudes"},
    {"module": "request", "action": "exportar", "description": "Exportar solicitudes"},
    {"module": "request", "action": "cancelar", "description": "Cancelar solicitudes"},

    # Offer
    {"module": "offer", "action": "ver", "description": "Ver ofertas"},
    {"module": "offer", "action": "crear", "description": "Crear ofertas"},
    {"module": "offer", "action": "editar", "description": "Editar ofertas"},
    {"module": "offer", "action": "eliminar", "description": "Eliminar ofertas"},
    {"module": "offer", "action": "exportar", "description": "Exportar ofertas"},
    {"module": "offer", "action": "importar", "description": "Importar ofertas"},
    {"module": "offer", "action": "ver_historial", "description": "Ver historial de precios"},

    # Opportunity
    {"module": "opportunity", "action": "ver", "description": "Ver oportunidades"},
    {"module": "opportunity", "action": "crear", "description": "Crear oportunidades"},
    {"module": "opportunity", "action": "editar", "description": "Editar oportunidades"},
    {"module": "opportunity", "action": "eliminar", "description": "Eliminar oportunidades"},
    {"module": "opportunity", "action": "aceptar", "description": "Aceptar oportunidades"},
    {"module": "opportunity", "action": "descartar", "description": "Descartar oportunidades"},
    {"module": "opportunity", "action": "ejecutar", "description": "Ejecutar oportunidades"},
    {"module": "opportunity", "action": "exportar", "description": "Exportar oportunidades"},

    # Resource
    {"module": "resource", "action": "ver", "description": "Ver recursos"},
    {"module": "resource", "action": "crear", "description": "Crear recursos"},
    {"module": "resource", "action": "editar", "description": "Editar recursos"},
    {"module": "resource", "action": "eliminar", "description": "Eliminar recursos"},

    # Supplier
    {"module": "supplier", "action": "ver", "description": "Ver proveedores"},
    {"module": "supplier", "action": "crear", "description": "Crear proveedores"},
    {"module": "supplier", "action": "editar", "description": "Editar proveedores"},
    {"module": "supplier", "action": "eliminar", "description": "Eliminar proveedores"},

    # Warehouse
    {"module": "warehouse", "action": "ver", "description": "Ver almacenes"},
    {"module": "warehouse", "action": "crear", "description": "Crear almacenes"},
    {"module": "warehouse", "action": "editar", "description": "Editar almacenes"},
    {"module": "warehouse", "action": "eliminar", "description": "Eliminar almacenes"},

    # Movement
    {"module": "movement", "action": "ver", "description": "Ver movimientos"},
    {"module": "movement", "action": "crear", "description": "Crear movimientos"},

    # Purchase Request
    {"module": "purchase_request", "action": "ver", "description": "Ver solicitudes"},
    {"module": "purchase_request", "action": "crear", "description": "Crear solicitudes"},
    {"module": "purchase_request", "action": "editar", "description": "Editar solicitudes"},
    {"module": "purchase_request", "action": "eliminar", "description": "Eliminar solicitudes"},
    {"module": "purchase_request", "action": "aprobar", "description": "Aprobar solicitudes"},
    {"module": "purchase_request", "action": "recibir", "description": "Recibir mercancía"},

    # Supplier Quote
    {"module": "supplier_quote", "action": "ver", "description": "Ver cotizaciones"},
    {"module": "supplier_quote", "action": "crear", "description": "Crear cotizaciones"},
    {"module": "supplier_quote", "action": "editar", "description": "Editar cotizaciones"},
    {"module": "supplier_quote", "action": "eliminar", "description": "Eliminar cotizaciones"},
    {"module": "supplier_quote", "action": "seleccionar", "description": "Seleccionar cotización"},

    # Tenant
    {"module": "tenant", "action": "configurar", "description": "Configurar tenant"},
    {"module": "tenant", "action": "ver_usuarios", "description": "Ver usuarios"},
    {"module": "tenant", "action": "invitar_usuarios", "description": "Invitar usuarios"},
    {"module": "tenant", "action": "gestionar_roles", "description": "Gestionar roles"},
    {"module": "tenant", "action": "gestionar_permisos", "description": "Gestionar permisos"},
    {"module": "tenant", "action": "ver_logs", "description": "Ver logs"},
    {"module": "tenant", "action": "exportar_todo", "description": "Exportar todos los datos"},
    {"module": "tenant", "action": "eliminar", "description": "Eliminar tenant"},

    # Availability
    {"module": "availability", "action": "ver", "description": "Ver disponibilidad"},

    # Production
    {"module": "production", "action": "ver", "description": "Ver producción"},
    {"module": "production", "action": "crear", "description": "Crear producción"},
    {"module": "production", "action": "editar", "description": "Editar producción"},
    {"module": "production", "action": "eliminar", "description": "Eliminar producción"},
]


def seed_permissions(db: Session) -> int:
    """Crea los permisos iniciales. Idempotente."""
    count = 0
    for data in PERMISSIONS:
        existing = (
            db.query(Permission)
            .filter(
                Permission.module == data["module"],
                Permission.action == data["action"],
            )
            .first()
        )
        if not existing:
            db.add(Permission(**data))
            db.flush()  # Flush para que el siguiente existing lo detecte
            count += 1
    db.commit()
    return count