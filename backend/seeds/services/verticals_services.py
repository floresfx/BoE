"""Seed de la relacion vertical <-> servicio.

Resuelve vertical_code y service_code -> UUIDs.
"""

from sqlalchemy.orm import Session

from app.models import ServiceTemplate, Vertical, VerticalService


VERTICALS_SERVICES = [
    # Clinicas generales
    ("clinicas_generales", "consulta_medica", 1),
    ("clinicas_generales", "consulta_especialidad", 2),
    ("clinicas_generales", "laboratorio_clinico", 3),
    ("clinicas_generales", "imagenologia", 4),
    ("clinicas_generales", "urgencias", 5),
    ("clinicas_generales", "cirugia_ambulatoria", 6),
    ("clinicas_generales", "vacunacion", 7),
    ("clinicas_generales", "rehabilitacion", 8),
    ("clinicas_generales", "chequeo_preventivo", 9),
    # Clinicas dentales
    ("clinicas_dentales", "odontologia_general", 1),
    ("clinicas_dentales", "ortodoncia", 2),
    ("clinicas_dentales", "implantologia", 3),
    ("clinicas_dentales", "protesis_dental", 4),
    ("clinicas_dentales", "estetica_dental", 5),
    ("clinicas_dentales", "endodoncia", 6),
    ("clinicas_dentales", "periodoncia", 7),
    ("clinicas_dentales", "odontopediatria", 8),
    ("clinicas_dentales", "cirugia_oral", 9),
    ("clinicas_dentales", "radiologia_dental", 10),
    # Panaderias
    ("panaderias", "panes_artesanales", 1),
    ("panaderias", "panes_especiales", 2),
    ("panaderias", "bolleria", 3),
    ("panaderias", "pasteleria", 4),
    ("panaderias", "productos_salados", 5),
    # Restaurantes
    ("restaurantes", "platos_carta", 1),
    ("restaurantes", "bebidas_cocteleria", 2),
    ("restaurantes", "menu_dia", 3),
    ("restaurantes", "reposteria_postres", 4),
    ("restaurantes", "productos_gourmet", 5),
    # Fabricantes
    ("fabricantes", "bienes_consumo_final", 1),
    ("fabricantes", "bienes_intermedios", 2),
    ("fabricantes", "materias_primas_procesadas", 3),
    ("fabricantes", "maquinaria_equipo", 4),
    ("fabricantes", "embalajes_envases", 5),
    ("fabricantes", "maquila", 6),
    ("fabricantes", "marca_blanca", 7),
    ("fabricantes", "corte_mecanizado", 8),
    ("fabricantes", "copacking", 9),
    ("fabricantes", "prototipos", 10),
    # Instituciones educativas
    ("instituciones_educativas", "programas_academicos", 1),
    ("instituciones_educativas", "educacion_continua", 2),
    ("instituciones_educativas", "tutorias", 3),
    ("instituciones_educativas", "orientacion_psicologica", 4),
    ("instituciones_educativas", "bolsa_trabajo", 5),
    ("instituciones_educativas", "actividades_extracurriculares", 6),
    ("instituciones_educativas", "certificaciones", 7),
    ("instituciones_educativas", "plataforma_lms", 8),
    ("instituciones_educativas", "merchandising_edu", 9),
    # Proyectos por encargo
    ("proyectos_por_encargo", "planificacion_eventos", 1),
    ("proyectos_por_encargo", "diseno_evento", 2),
    ("proyectos_por_encargo", "gestion_proveedores", 3),
    ("proyectos_por_encargo", "secretaria_tecnica", 4),
    ("proyectos_por_encargo", "produccion_audiovisual", 5),
    ("proyectos_por_encargo", "protocolo_rrpp", 6),
    ("proyectos_por_encargo", "stands_escenografia", 7),
    ("proyectos_por_encargo", "ambientacion_floral", 8),
    ("proyectos_por_encargo", "papeleria_fina", 9),
    ("proyectos_por_encargo", "material_promocional", 10),
    ("proyectos_por_encargo", "contenido_post_evento", 11),
    # Empresas de limpieza
    ("empresas_limpieza", "limpieza_mantenimiento", 1),
    ("empresas_limpieza", "limpieza_profunda", 2),
    ("empresas_limpieza", "desinfeccion", 3),
    ("empresas_limpieza", "limpieza_cristales", 4),
    ("empresas_limpieza", "tratamiento_suelos", 5),
    ("empresas_limpieza", "lavado_tapiceria", 6),
    ("empresas_limpieza", "quimicos_limpieza", 7),
    ("empresas_limpieza", "utiles_limpieza", 8),
    ("empresas_limpieza", "consumibles_higienicos", 9),
    ("empresas_limpieza", "dispensadores", 10),
    ("empresas_limpieza", "maquinaria_limpieza", 11),
    # Empresas de mantenimiento
    ("empresas_mantenimiento", "mant_edilicio", 1),
    ("empresas_mantenimiento", "mant_electrico", 2),
    ("empresas_mantenimiento", "mant_hvac", 3),
    ("empresas_mantenimiento", "mant_mecanico", 4),
    ("empresas_mantenimiento", "mant_seguridad", 5),
    ("empresas_mantenimiento", "mant_preventivo", 6),
    ("empresas_mantenimiento", "repuestos", 7),
    ("empresas_mantenimiento", "herramientas_industriales", 8),
    ("empresas_mantenimiento", "lubricantes", 9),
    ("empresas_mantenimiento", "materiales_fijacion", 10),
    ("empresas_mantenimiento", "epp", 11),
    # Empresas de transporte
    ("empresas_transporte", "carga_local", 1),
    ("empresas_transporte", "carga_nacional", 2),
    ("empresas_transporte", "carga_internacional", 3),
    ("empresas_transporte", "carga_especial", 4),
    ("empresas_transporte", "paqueteria", 5),
    ("empresas_transporte", "carga_pesada", 6),
    ("empresas_transporte", "transporte_refrigerado", 7),
    ("empresas_transporte", "almacenaje", 8),
    ("empresas_transporte", "transporte_pasajeros", 9),
    ("empresas_transporte", "embalajes_proteccion", 10),
    ("empresas_transporte", "contenedores", 11),
    ("empresas_transporte", "gps_rastreo", 12),
    ("empresas_transporte", "flotas_usadas", 13),
    # Hoteles
    ("hoteles", "estadia_estandar", 1),
    ("hoteles", "estadia_suite", 2),
    ("hoteles", "paquete_turistico", 3),
    ("hoteles", "eventos_hotel", 4),
    ("hoteles", "restaurante_hotel", 5),
    # Heladerias
    ("heladerias", "helado_artesanal", 1),
    ("heladerias", "gelato", 2),
    ("heladerias", "soft_serve", 3),
    ("heladerias", "frozen_yogurt", 4),
    ("heladerias", "paletas", 5),
    ("heladerias", "malteadas", 6),
    ("heladerias", "postres_helados", 7),
    ("heladerias", "toppings", 8),
    # Talleres
    ("talleres", "mant_auto_preventivo", 1),
    ("talleres", "diagnostico_auto", 2),
    ("talleres", "reparacion_frenos", 3),
    ("talleres", "suspension_direccion", 4),
    ("talleres", "reparacion_motor", 5),
    ("talleres", "electricidad_auto", 6),
    ("talleres", "aire_acondicionado_auto", 7),
    ("talleres", "hojalateria_pintura", 8),
    ("talleres", "refacciones_auto", 9),
    ("talleres", "llantas", 10),
    ("talleres", "baterias_auto", 11),
    ("talleres", "fluidos_auto", 12),
    ("talleres", "accesorios_auto", 13),
    # Ferreterias
    ("ferreterias", "ferreteria_general", 1),
    ("ferreterias", "materiales_construccion", 2),
    ("ferreterias", "pintura_ferreteria", 3),
    ("ferreterias", "plomeria_ferreteria", 4),
    ("ferreterias", "electricidad_ferreteria", 5),
    ("ferreterias", "herramientas_manuales", 6),
    ("ferreterias", "herramientas_electricas", 7),
    ("ferreterias", "jardin_ferreteria", 8),
    # Distribuidoras
    ("distribuidoras", "consumo_masivo", 1),
    ("distribuidoras", "farmaceuticos", 2),
    ("distribuidoras", "construccion_mayorista", 3),
    ("distribuidoras", "tecnologia_mayorista", 4),
    ("distribuidoras", "suministros_industriales", 5),
    # Laboratorios
    ("laboratorios", "analisis_clinicos", 1),
    ("laboratorios", "pruebas_microbiologicas", 2),
    ("laboratorios", "control_calidad", 3),
    ("laboratorios", "analisis_ambientales", 4),
    ("laboratorios", "estabilidad_caducidad", 5),
    ("laboratorios", "calibracion_equipos", 6),
    ("laboratorios", "fabricacion_farma", 7),
    ("laboratorios", "reactivos_quimicos", 8),
    ("laboratorios", "kits_diagnostico", 9),
    ("laboratorios", "medios_cultivo", 10),
    ("laboratorios", "materiales_referencia", 11),
    # Academias
    ("academias", "curso_corto", 1),
    ("academias", "taller_intensivo", 2),
    ("academias", "clase_magistral", 3),
    ("academias", "certificacion_prof", 4),
    ("academias", "bootcamp", 5),
    # Construccion
    ("construccion", "construccion_residencial", 1),
    ("construccion", "construccion_comercial", 2),
    ("construccion", "obras_civiles", 3),
    ("construccion", "remodelacion", 4),
    ("construccion", "llave_en_mano", 5),
    ("construccion", "demolicion", 6),
    ("construccion", "estructuras_metalicas", 7),
    ("construccion", "concreto_preparado", 8),
    ("construccion", "materiales_petreos", 9),
    ("construccion", "planos_3d", 10),
    # Diseno
    ("diseño", "branding", 1),
    ("diseño", "diseno_web_ux", 2),
    ("diseño", "diseno_interiores", 3),
    ("diseño", "packaging_diseno", 4),
    ("diseño", "editorial", 5),
    ("diseño", "consultoria_diseno", 6),
    ("diseño", "manuales_marca", 7),
    ("diseño", "assets_digitales", 8),
    ("diseño", "prototipos_3d", 9),
    ("diseño", "patrones_fichas", 10),
    ("diseño", "ilustraciones", 11),
]


def seed_verticals_services(db: Session) -> int:
    """Crea la relacion vertical <-> servicio. Idempotente."""
    count = 0

    verticals = {v.code: v for v in db.query(Vertical).all()}
    services = {s.code: s for s in db.query(ServiceTemplate).all()}

    for vertical_code, service_code, order in VERTICALS_SERVICES:
        vertical = verticals.get(vertical_code)
        service = services.get(service_code)

        if not vertical or not service:
            raise ValueError(
                f"No encontrado: {vertical_code} <-> {service_code}"
            )

        existing = (
            db.query(VerticalService)
            .filter(
                VerticalService.vertical_id == vertical.id,
                VerticalService.service_id == service.id,
            )
            .first()
        )
        if existing:
            continue

        db.add(
            VerticalService(
                vertical_id=vertical.id,
                service_id=service.id,
                display_order=order,
            )
        )
        count += 1

    db.commit()
    return count