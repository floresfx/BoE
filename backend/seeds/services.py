# seeds/services.py

from sqlalchemy.orm import Session

from app.models import ServiceTemplate, Vertical, VerticalService


# =============================================================================
# CATÁLOGO DE SERVICIOS (171 servicios)
# =============================================================================
SERVICE_TEMPLATES = [
    # --- SALUD: Clínicas generales (1-10) ---
    {"code": "consulta_medica", "name": "Consulta médica", "description": "Evaluación inicial, recetas y control", "category_code": "salud"},
    {"code": "consulta_especialidad", "name": "Consulta de especialidad", "description": "Pediatría, ginecología, cardiología, dermatología", "category_code": "salud"},
    {"code": "laboratorio_clinico", "name": "Laboratorio clínico", "description": "Análisis de sangre, orina y fluidos", "category_code": "salud"},
    {"code": "imagenologia", "name": "Imagenología", "description": "Radiografías, ecografías, TAC, resonancias", "category_code": "salud"},
    {"code": "urgencias", "name": "Atención de urgencias", "description": "Primeros auxilios y estabilización", "category_code": "salud"},
    {"code": "observacion", "name": "Unidad de observación", "description": "Monitoreo por horas", "category_code": "salud"},
    {"code": "cirugia_ambulatoria", "name": "Cirugía ambulatoria", "description": "Operaciones sin hospitalización", "category_code": "salud"},
    {"code": "vacunacion", "name": "Vacunación", "description": "Vacunas preventivas", "category_code": "salud"},
    {"code": "rehabilitacion", "name": "Rehabilitación y terapias", "description": "Fisioterapia, terapia respiratoria", "category_code": "salud"},
    {"code": "chequeo_preventivo", "name": "Chequeos preventivos", "description": "Evaluaciones médicas de rutina", "category_code": "salud"},

    # --- SALUD: Clínicas dentales (11-20) ---
    {"code": "odontologia_general", "name": "Odontología general", "description": "Revisiones, limpiezas, empastes", "category_code": "salud"},
    {"code": "ortodoncia", "name": "Ortodoncia", "description": "Brackets, alineadores", "category_code": "salud"},
    {"code": "implantologia", "name": "Implantología", "description": "Implantes de titanio", "category_code": "salud"},
    {"code": "protesis_dental", "name": "Prótesis dentales", "description": "Coronas, puentes, dentaduras", "category_code": "salud"},
    {"code": "estetica_dental", "name": "Estética dental", "description": "Blanqueamientos, carillas", "category_code": "salud"},
    {"code": "endodoncia", "name": "Endodoncia", "description": "Tratamiento de nervio", "category_code": "salud"},
    {"code": "periodoncia", "name": "Periodoncia", "description": "Tratamiento de encías", "category_code": "salud"},
    {"code": "odontopediatria", "name": "Odontopediatría", "description": "Odontología infantil", "category_code": "salud"},
    {"code": "cirugia_oral", "name": "Cirugía oral", "description": "Extracciones complejas", "category_code": "salud"},
    {"code": "radiologia_dental", "name": "Radiología dental", "description": "Radiografías dentales", "category_code": "salud"},

    # --- COMIDA: Panaderías (21-25) ---
    {"code": "panes_artesanales", "name": "Panes tradicionales y artesanales", "description": "Baguette, masa madre, pan campesino", "category_code": "comida"},
    {"code": "panes_especiales", "name": "Panes especiales y de molde", "description": "Integral, centeno, sin gluten, dulces", "category_code": "comida"},
    {"code": "bolleria", "name": "Bollería y panadería dulce", "description": "Croissants, berlinas, donuts, muffins", "category_code": "comida"},
    {"code": "pasteleria", "name": "Pastelería y repostería", "description": "Tartas, pasteles, bizcochos, galletas", "category_code": "comida"},
    {"code": "productos_salados", "name": "Productos salados horneados", "description": "Empanadas, quiches, pizzas, hojaldres", "category_code": "comida"},

    # --- COMIDA: Restaurantes (26-30) ---
    {"code": "platos_carta", "name": "Platos a la carta", "description": "Entradas, platos fuertes, guarniciones", "category_code": "comida"},
    {"code": "bebidas_cocteleria", "name": "Bebidas y coctelería", "description": "Jugos, cafés, cócteles, vinos", "category_code": "comida"},
    {"code": "menu_dia", "name": "Menús del día o ejecutivos", "description": "Paquete cerrado: entrada, plato, bebida, postre", "category_code": "comida"},
    {"code": "reposteria_postres", "name": "Repostería y postres caseros", "description": "Dulces, tartas, helados", "category_code": "comida"},
    {"code": "productos_gourmet", "name": "Productos gourmet o de marca propia", "description": "Salsas, aderezos, aceites, envasados", "category_code": "comida"},

    # --- OTROS: Fabricantes (31-40) ---
    {"code": "bienes_consumo_final", "name": "Bienes de consumo final", "description": "Alimentos empacados, ropa, electrodomésticos", "category_code": "otros"},
    {"code": "bienes_intermedios", "name": "Bienes intermedios (componentes)", "description": "Chips, láminas de acero, piezas", "category_code": "otros"},
    {"code": "materias_primas_procesadas", "name": "Materias primas procesadas", "description": "Cemento, harinas, combustibles", "category_code": "otros"},
    {"code": "maquinaria_equipo", "name": "Maquinaria y bienes de equipo", "description": "Tractores, prensas, brazos robóticos", "category_code": "otros"},
    {"code": "embalajes_envases", "name": "Embalajes y envases", "description": "Cajas, botellas, latas, frascos", "category_code": "otros"},
    {"code": "maquila", "name": "Fabricación por contrato (Maquila)", "description": "Producción para marca externa", "category_code": "otros"},
    {"code": "marca_blanca", "name": "Producción de marca blanca", "description": "Productos genéricos con marca del cliente", "category_code": "otros"},
    {"code": "corte_mecanizado", "name": "Corte y mecanizado a la medida", "description": "Láser, CNC, chorro de agua", "category_code": "otros"},
    {"code": "copacking", "name": "Envasado y empaquetado externo", "description": "Dosificación y empaque", "category_code": "otros"},
    {"code": "prototipos", "name": "Diseño y desarrollo de prototipos", "description": "Modelos físicos o moldes", "category_code": "otros"},

    # --- EDUCACIÓN: Instituciones educativas (41-49) ---
    {"code": "programas_academicos", "name": "Programas académicos y docencia", "description": "Clases teóricas y prácticas con título", "category_code": "educacion"},
    {"code": "educacion_continua", "name": "Educación continua y cursos libres", "description": "Talleres, diplomados, cursos cortos", "category_code": "educacion"},
    {"code": "tutorias", "name": "Tutorías y orientación académica", "description": "Asesorías personalizadas o grupales", "category_code": "educacion"},
    {"code": "orientacion_psicologica", "name": "Orientación psicológica", "description": "Apoyo profesional a alumnos", "category_code": "educacion"},
    {"code": "bolsa_trabajo", "name": "Bolsa de trabajo y prácticas", "description": "Vinculación con empresas", "category_code": "educacion"},
    {"code": "actividades_extracurriculares", "name": "Actividades extracurriculares", "description": "Deportes, artes, clubes", "category_code": "educacion"},
    {"code": "certificaciones", "name": "Certificaciones y títulos oficiales", "description": "Diplomas, actas con validez legal", "category_code": "educacion"},
    {"code": "plataforma_lms", "name": "Plataformas de aprendizaje virtual", "description": "Aulas digitales, contenidos, tareas", "category_code": "educacion"},
    {"code": "merchandising_edu", "name": "Artículos de identidad institucional", "description": "Uniformes, cuadernos, papelería", "category_code": "educacion"},

    # --- OTROS: Proyectos por encargo (50-60) ---
    {"code": "planificacion_eventos", "name": "Planificación y coordinación integral", "description": "Gestión del proyecto completo", "category_code": "otros"},
    {"code": "diseño_evento", "name": "Diseño y conceptualización del evento", "description": "Identidad visual, temática", "category_code": "otros"},
    {"code": "gestion_proveedores", "name": "Gestión de proveedores y contratación", "description": "Venue sourcing, catering, fotografía", "category_code": "otros"},
    {"code": "secretaria_tecnica", "name": "Secretaría técnica y registro", "description": "RSVP, venta de entradas, acreditación", "category_code": "otros"},
    {"code": "produccion_audiovisual", "name": "Producción técnica y audiovisual", "description": "Sonido, iluminación, streaming", "category_code": "otros"},
    {"code": "protocolo_rrpp", "name": "Protocolo y relaciones públicas", "description": "Agenda, VIPs, prensa", "category_code": "otros"},
    {"code": "stands_escenografia", "name": "Diseño y construcción de stands", "description": "Estructuras personalizadas", "category_code": "otros"},
    {"code": "ambientacion_floral", "name": "Ambientación y decoración floral", "description": "Centros de mesa, altares, ramos", "category_code": "otros"},
    {"code": "papeleria_fina", "name": "Papelería fina y cartelería", "description": "Invitaciones, minutas, señalética", "category_code": "otros"},
    {"code": "material_promocional", "name": "Material promocional y corporativo", "description": "Kits de bienvenida, recuerdos", "category_code": "otros"},
    {"code": "contenido_post_evento", "name": "Contenido audiovisual post-evento", "description": "Fotografías, videos, memorias", "category_code": "otros"},

    # --- SERVICIOS: Empresas de limpieza (61-71) ---
    {"code": "limpieza_mantenimiento", "name": "Limpieza de mantenimiento", "description": "Servicio periódico (diario/semanal)", "category_code": "servicios"},
    {"code": "limpieza_profunda", "name": "Limpieza profunda o de fin de obra", "description": "Intervención exhaustiva", "category_code": "servicios"},
    {"code": "desinfeccion", "name": "Desinfección y sanitización", "description": "Productos grado hospitalario", "category_code": "servicios"},
    {"code": "limpieza_cristales", "name": "Limpieza de cristales y fachadas", "description": "Ventanas, mamparas, vidrios", "category_code": "servicios"},
    {"code": "tratamiento_suelos", "name": "Tratamiento y abrillantado de suelos", "description": "Decapado, pulido, encerado", "category_code": "servicios"},
    {"code": "lavado_tapiceria", "name": "Lavado de alfombras y tapizados", "description": "Alfombras, sillas, sillones, colchones", "category_code": "servicios"},
    {"code": "quimicos_limpieza", "name": "Químicos de limpieza profesionales", "description": "Detergentes, desengrasantes, desinfectantes", "category_code": "servicios"},
    {"code": "utiles_limpieza", "name": "Útiles y herramientas de limpieza", "description": "Mopas, escobas, paños, carros", "category_code": "servicios"},
    {"code": "consumibles_higienicos", "name": "Consumibles higiénicos", "description": "Papel higiénico, toallas, jabón", "category_code": "servicios"},
    {"code": "dispensadores", "name": "Dispensadores y dosificadores", "description": "Jabón, gel, papel, ambientadores", "category_code": "servicios"},
    {"code": "maquinaria_limpieza", "name": "Maquinaria industrial de limpieza", "description": "Aspiradoras, hidrolimpiadoras, barredoras", "category_code": "servicios"},

    # --- SERVICIOS: Empresas de mantenimiento (72-82) ---
    {"code": "mant_edilicio", "name": "Mantenimiento edilicio", "description": "Pintura, albañilería, plomería, techos", "category_code": "servicios"},
    {"code": "mant_electrico", "name": "Mantenimiento eléctrico", "description": "Tableros, cableado, luminarias", "category_code": "servicios"},
    {"code": "mant_hvac", "name": "Mantenimiento de climatización (HVAC)", "description": "Aire acondicionado, calefacción, ventilación", "category_code": "servicios"},
    {"code": "mant_mecanico", "name": "Mantenimiento mecánico industrial", "description": "Maquinaria, motores, bandas", "category_code": "servicios"},
    {"code": "mant_seguridad", "name": "Mantenimiento de seguridad y contra incendios", "description": "CCTV, alarmas, extintores", "category_code": "servicios"},
    {"code": "mant_preventivo", "name": "Mantenimiento preventivo programado", "description": "Visitas periódicas con checklist", "category_code": "servicios"},
    {"code": "repuestos", "name": "Piezas de repuesto y consumibles", "description": "Filtros, bujías, correas, válvulas", "category_code": "servicios"},
    {"code": "herramientas_industriales", "name": "Herramientas y ferretería industrial", "description": "Manuales, eléctricas, neumáticas", "category_code": "servicios"},
    {"code": "lubricantes", "name": "Lubricantes y químicos técnicos", "description": "Aceites, grasas, refrigerantes", "category_code": "servicios"},
    {"code": "materiales_fijacion", "name": "Materiales de fijación y ferretería", "description": "Tornillos, pernos, anclajes, siliconas", "category_code": "servicios"},
    {"code": "epp", "name": "Equipos e insumos de seguridad (EPP)", "description": "Cascos, guantes, calzado, arneses", "category_code": "servicios"},

    # --- SERVICIOS: Empresas de transporte (83-95) ---
    {"code": "carga_local", "name": "Transporte de carga general local", "description": "Envío por vía terrestre local", "category_code": "servicios"},
    {"code": "carga_nacional", "name": "Transporte de carga general nacional", "description": "Envío terrestre nacional", "category_code": "servicios"},
    {"code": "carga_internacional", "name": "Transporte de carga general internacional", "description": "Terrestre, marítimo, aéreo", "category_code": "servicios"},
    {"code": "carga_especial", "name": "Transporte de carga especial", "description": "Maquinaria pesada, estructuras", "category_code": "servicios"},
    {"code": "paqueteria", "name": "Paquetería y mensajería express", "description": "Sobres, documentos, paquetes", "category_code": "servicios"},
    {"code": "carga_pesada", "name": "Transporte de carga pesada", "description": "Plataformas especializadas", "category_code": "servicios"},
    {"code": "transporte_refrigerado", "name": "Transporte refrigerado (cadena de frío)", "description": "Perecederos, medicinas, químicos", "category_code": "servicios"},
    {"code": "almacenaje", "name": "Almacenaje y gestión de inventarios", "description": "Bodegas logísticas", "category_code": "servicios"},
    {"code": "transporte_pasajeros", "name": "Transporte de pasajeros", "description": "Público, corporativo, escolar, turístico", "category_code": "servicios"},
    {"code": "embalajes_proteccion", "name": "Embalajes y materiales de protección", "description": "Cajas, palés, burbujas, cintas", "category_code": "servicios"},
    {"code": "contenedores", "name": "Venta o alquiler de contenedores", "description": "Contenedores 20/40 pies, reefers", "category_code": "servicios"},
    {"code": "gps_rastreo", "name": "Sistemas y software de rastreo (GPS)", "description": "Dispositivos y plataformas", "category_code": "servicios"},
    {"code": "flotas_usadas", "name": "Flotas vehiculares usadas o repuestos", "description": "Camiones, furgonetas, componentes", "category_code": "servicios"},

    # --- SERVICIOS: Hoteles (96-100) ---
    {"code": "estadia_estandar", "name": "Estadía estándar", "description": "Habitación estándar con servicios básicos", "category_code": "servicios"},
    {"code": "estadia_suite", "name": "Estadía en suite", "description": "Habitación premium con amenities", "category_code": "servicios"},
    {"code": "paquete_turistico", "name": "Paquete turístico", "description": "Alojamiento + actividades", "category_code": "servicios"},
    {"code": "eventos_hotel", "name": "Eventos y conferencias", "description": "Salones, catering, audiovisual", "category_code": "servicios"},
    {"code": "restaurante_hotel", "name": "Restaurante y bar", "description": "Comidas y bebidas en el hotel", "category_code": "servicios"},

    # --- COMIDA: Heladerías (101-108) ---
    {"code": "helado_artesanal", "name": "Helados artesanales", "description": "Conos, vasos, tarrinas", "category_code": "comida"},
    {"code": "gelato", "name": "Gelato italiano", "description": "Textura densa, menos grasa", "category_code": "comida"},
    {"code": "soft_serve", "name": "Helado suave (Soft Serve)", "description": "Máquina de palanca", "category_code": "comida"},
    {"code": "frozen_yogurt", "name": "Yogur helado", "description": "Base de yogur, con toppings", "category_code": "comida"},
    {"code": "paletas", "name": "Paletas o polos", "description": "Helados con palito", "category_code": "comida"},
    {"code": "malteadas", "name": "Malteadas y batidos", "description": "Bebidas frías con helado", "category_code": "comida"},
    {"code": "postres_helados", "name": "Pasteles y postres helados", "description": "Tortas, Banana Split, copas", "category_code": "comida"},
    {"code": "toppings", "name": "Toppings y coberturas", "description": "Frutas, frutos secos, siropes", "category_code": "comida"},

    # --- SERVICIOS: Talleres (109-121) ---
    {"code": "mant_auto_preventivo", "name": "Mantenimiento preventivo (afinación)", "description": "Aceite, filtros, revisión de niveles", "category_code": "servicios"},
    {"code": "diagnostico_auto", "name": "Diagnóstico por computadora", "description": "Escaneo electrónico", "category_code": "servicios"},
    {"code": "reparacion_frenos", "name": "Reparación de frenos", "description": "Discos, balatas, líquido", "category_code": "servicios"},
    {"code": "suspension_direccion", "name": "Suspensión y dirección", "description": "Amortiguadores, alineación, balanceo", "category_code": "servicios"},
    {"code": "reparacion_motor", "name": "Reparación de motor y transmisión", "description": "Bandas, empaques, cajas", "category_code": "servicios"},
    {"code": "electricidad_auto", "name": "Electricidad y electrónica automotriz", "description": "Marcha, alternador, baterías", "category_code": "servicios"},
    {"code": "aire_acondicionado_auto", "name": "Aire acondicionado automotriz", "description": "Recarga de gas, compresores", "category_code": "servicios"},
    {"code": "hojalateria_pintura", "name": "Hojalatería y pintura", "description": "Abolladuras, pintura automotriz", "category_code": "servicios"},
    {"code": "refacciones_auto", "name": "Refacciones y componentes", "description": "Bujías, balatas, filtros, bombas", "category_code": "servicios"},
    {"code": "llantas", "name": "Llantas y neumáticos", "description": "Marcas, medidas, rangos", "category_code": "servicios"},
    {"code": "baterias_auto", "name": "Baterías automotrices", "description": "Acumuladores", "category_code": "servicios"},
    {"code": "fluidos_auto", "name": "Fluidos y lubricantes", "description": "Aceites, frenos, refrigerantes", "category_code": "servicios"},
    {"code": "accesorios_auto", "name": "Accesorios y consumibles menores", "description": "Plumillas, focos, fusibles", "category_code": "servicios"},

    # --- OTROS: Ferreterías (122-129) ---
    {"code": "ferreteria_general", "name": "Ferretería general", "description": "Herramientas, materiales, tornillería", "category_code": "otros"},
    {"code": "materiales_construccion", "name": "Materiales de construcción", "description": "Cemento, cabillas, bloques, arena", "category_code": "otros"},
    {"code": "pintura_ferreteria", "name": "Pintura y acabados", "description": "Pinturas, barnices, solventes", "category_code": "otros"},
    {"code": "plomeria_ferreteria", "name": "Plomería y grifería", "description": "Tuberías, conexiones, llaves", "category_code": "otros"},
    {"code": "electricidad_ferreteria", "name": "Electricidad y cableado", "description": "Cables, breakers, tomacorrientes", "category_code": "otros"},
    {"code": "herramientas_manuales", "name": "Herramientas manuales", "description": "Martillos, destornilladores, llaves", "category_code": "otros"},
    {"code": "herramientas_electricas", "name": "Herramientas eléctricas", "description": "Taladros, sierras, esmeriles", "category_code": "otros"},
    {"code": "jardin_ferreteria", "name": "Jardín y exterior", "description": "Mangueras, cortadoras, semillas", "category_code": "otros"},

    # --- OTROS: Distribuidoras (130-134) ---
    {"code": "consumo_masivo", "name": "Bienes de consumo masivo", "description": "Alimentos, bebidas, limpieza, aseo", "category_code": "otros"},
    {"code": "farmaceuticos", "name": "Productos farmacéuticos y médicos", "description": "Medicamentos, material de curación", "category_code": "salud"},
    {"code": "construccion_mayorista", "name": "Materiales de construcción y ferretería", "description": "Mayoreo para tiendas y constructoras", "category_code": "otros"},
    {"code": "tecnologia_mayorista", "name": "Componentes tecnológicos y electrónicos", "description": "Computación, móviles, electrodomésticos", "category_code": "tecnologia"},
    {"code": "suministros_industriales", "name": "Suministros industriales y materias primas", "description": "Químicos, lubricantes, envases", "category_code": "otros"},

    # --- SALUD: Laboratorios (135-145) ---
    {"code": "analisis_clinicos", "name": "Análisis clínicos y de salud", "description": "Sangre, orina, tejidos, ADN", "category_code": "salud"},
    {"code": "pruebas_microbiologicas", "name": "Pruebas microbiológicas", "description": "Bacterias, hongos, virus", "category_code": "salud"},
    {"code": "control_calidad", "name": "Control de calidad y ensayos industriales", "description": "Resistencia, pureza, composición", "category_code": "otros"},
    {"code": "analisis_ambientales", "name": "Análisis ambientales", "description": "Agua, aire, suelos", "category_code": "otros"},
    {"code": "estabilidad_caducidad", "name": "Estudios de estabilidad y caducidad", "description": "Temperatura y humedad controladas", "category_code": "otros"},
    {"code": "calibracion_equipos", "name": "Calibración de equipos", "description": "Balanzas, termómetros, manómetros", "category_code": "otros"},
    {"code": "fabricacion_farma", "name": "Medicamentos y fórmulas farmacéuticas", "description": "Fármacos, jarabes, vacunas", "category_code": "salud"},
    {"code": "reactivos_quimicos", "name": "Reactivos químicos y soluciones", "description": "Compuestos para análisis", "category_code": "otros"},
    {"code": "kits_diagnostico", "name": "Kits de diagnóstico rápido", "description": "Embarazo, glucosa, antígenos", "category_code": "salud"},
    {"code": "medios_cultivo", "name": "Medios de cultivo", "description": "Agar, preparados nutritivos", "category_code": "otros"},
    {"code": "materiales_referencia", "name": "Materiales de referencia certificados", "description": "Muestras de pureza conocida", "category_code": "otros"},

    # --- EDUCACIÓN: Academias (146-150) ---
    {"code": "curso_corto", "name": "Curso corto", "description": "Formación específica de horas", "category_code": "educacion"},
    {"code": "taller_intensivo", "name": "Taller intensivo", "description": "Formación práctica concentrada", "category_code": "educacion"},
    {"code": "clase_magistral", "name": "Clase magistral", "description": "Sesión con experto", "category_code": "educacion"},
    {"code": "certificacion_prof", "name": "Certificación profesional", "description": "Acredita competencias", "category_code": "educacion"},
    {"code": "bootcamp", "name": "Bootcamp", "description": "Formación intensiva inmersiva", "category_code": "educacion"},

    # --- OTROS: Construcción (151-160) ---
    {"code": "construccion_residencial", "name": "Construcción residencial", "description": "Viviendas, conjuntos, edificios", "category_code": "otros"},
    {"code": "construccion_comercial", "name": "Construcción comercial y corporativa", "description": "Oficinas, centros comerciales, naves", "category_code": "otros"},
    {"code": "obras_civiles", "name": "Obras civiles e infraestructura", "description": "Carreteras, puentes, represas", "category_code": "otros"},
    {"code": "remodelacion", "name": "Remodelación, ampliación y restauración", "description": "Modificación de estructuras", "category_code": "otros"},
    {"code": "llave_en_mano", "name": "Diseño y desarrollo (Llave en mano)", "description": "Planos + permisos + obra", "category_code": "otros"},
    {"code": "demolicion", "name": "Demolición y preparación de terrenos", "description": "Derribo, excavación, nivelación", "category_code": "otros"},
    {"code": "estructuras_metalicas", "name": "Estructuras metálicas y prefabricadas", "description": "Vigas, naves, paneles, módulos", "category_code": "otros"},
    {"code": "concreto_preparado", "name": "Mezclas de concreto y hormigón", "description": "Concreto fresco en camiones", "category_code": "otros"},
    {"code": "materiales_petreos", "name": "Materiales de construcción pétreos", "description": "Arena, grava, piedra, asfalto", "category_code": "otros"},
    {"code": "planos_3d", "name": "Planos técnicos y modelos 3D", "description": "Maquetas, BIM, diseños", "category_code": "otros"},

    # --- OTROS: Diseño (161-171) ---
    {"code": "branding", "name": "Branding e identidad corporativa", "description": "Logo, paleta, tipografía, manual", "category_code": "otros"},
    {"code": "diseño_web_ux", "name": "Diseño web y aplicaciones (UX/UI)", "description": "Interfaz y experiencia", "category_code": "otros"},
    {"code": "diseño_interiores", "name": "Diseño de interiores", "description": "Espacios físicos, mobiliario", "category_code": "otros"},
    {"code": "packaging_diseño", "name": "Diseño de packaging", "description": "Envases, etiquetas, cajas", "category_code": "otros"},
    {"code": "editorial", "name": "Diseño editorial y maquetación", "description": "Revistas, libros, catálogos", "category_code": "otros"},
    {"code": "consultoria_diseño", "name": "Consultoría de diseño y dirección de arte", "description": "Asesoría estratégica", "category_code": "otros"},
    {"code": "manuales_marca", "name": "Manuales de marca y pautas", "description": "Documentos técnicos de uso", "category_code": "otros"},
    {"code": "assets_digitales", "name": "Assets digitales y plantillas", "description": "Posts, presentaciones, banners", "category_code": "otros"},
    {"code": "prototipos_3d", "name": "Prototipos y maquetas en 3D", "description": "Modelos digitales o físicos", "category_code": "otros"},
    {"code": "patrones_fichas", "name": "Patrones y fichas técnicas", "description": "Planos, especificaciones", "category_code": "otros"},
    {"code": "ilustraciones", "name": "Ilustraciones de autor y tipografías", "description": "Dibujos, fuentes, iconos", "category_code": "otros"},
]


# =============================================================================
# RELACIÓN VERTICAL -> SERVICIOS (granularidad gruesa)
# =============================================================================
VERTICAL_SERVICES = {
    "clinicas_generales": ["consulta_medica", "consulta_especialidad", "laboratorio_clinico", "imagenologia", "urgencias", "cirugia_ambulatoria", "vacunacion", "rehabilitacion", "chequeo_preventivo"],
    "clinicas_dentales": ["odontologia_general", "ortodoncia", "implantologia", "protesis_dental", "estetica_dental", "endodoncia", "periodoncia", "odontopediatria", "cirugia_oral", "radiologia_dental"],
    "panaderias": ["panes_artesanales", "panes_especiales", "bolleria", "pasteleria", "productos_salados"],
    "restaurantes": ["platos_carta", "bebidas_cocteleria", "menu_dia", "reposteria_postres", "productos_gourmet"],
    "fabricantes": ["bienes_consumo_final", "bienes_intermedios", "materias_primas_procesadas", "maquinaria_equipo", "embalajes_envases", "maquila", "marca_blanca", "corte_mecanizado", "copacking", "prototipos"],
    "instituciones_educativas": ["programas_academicos", "educacion_continua", "tutorias", "orientacion_psicologica", "bolsa_trabajo", "actividades_extracurriculares", "certificaciones", "plataforma_lms", "merchandising_edu"],
    "proyectos_por_encargo": ["planificacion_eventos", "diseño_evento", "gestion_proveedores", "secretaria_tecnica", "produccion_audiovisual", "protocolo_rrpp", "stands_escenografia", "ambientacion_floral", "papeleria_fina", "material_promocional", "contenido_post_evento"],
    "empresas_limpieza": ["limpieza_mantenimiento", "limpieza_profunda", "desinfeccion", "limpieza_cristales", "tratamiento_suelos", "lavado_tapiceria", "quimicos_limpieza", "utiles_limpieza", "consumibles_higienicos", "dispensadores", "maquinaria_limpieza"],
    "empresas_mantenimiento": ["mant_edilicio", "mant_electrico", "mant_hvac", "mant_mecanico", "mant_seguridad", "mant_preventivo", "repuestos", "herramientas_industriales", "lubricantes", "materiales_fijacion", "epp"],
    "empresas_transporte": ["carga_local", "carga_nacional", "carga_internacional", "carga_especial", "paqueteria", "carga_pesada", "transporte_refrigerado", "almacenaje", "transporte_pasajeros", "embalajes_proteccion", "contenedores", "gps_rastreo", "flotas_usadas"],
    "hoteles": ["estadia_estandar", "estadia_suite", "paquete_turistico", "eventos_hotel", "restaurante_hotel"],
    "heladerias": ["helado_artesanal", "gelato", "soft_serve", "frozen_yogurt", "paletas", "malteadas", "postres_helados", "toppings"],
    "talleres": ["mant_auto_preventivo", "diagnostico_auto", "reparacion_frenos", "suspension_direccion", "reparacion_motor", "electricidad_auto", "aire_acondicionado_auto", "hojalateria_pintura", "refacciones_auto", "llantas", "baterias_auto", "fluidos_auto", "accesorios_auto"],
    "ferreterias": ["ferreteria_general", "materiales_construccion", "pintura_ferreteria", "plomeria_ferreteria", "electricidad_ferreteria", "herramientas_manuales", "herramientas_electricas", "jardin_ferreteria"],
    "distribuidoras": ["consumo_masivo", "farmaceuticos", "construccion_mayorista", "tecnologia_mayorista", "suministros_industriales"],
    "laboratorios": ["analisis_clinicos", "pruebas_microbiologicas", "control_calidad", "analisis_ambientales", "estabilidad_caducidad", "calibracion_equipos", "fabricacion_farma", "reactivos_quimicos", "kits_diagnostico", "medios_cultivo", "materiales_referencia"],
    "academias": ["curso_corto", "taller_intensivo", "clase_magistral", "certificacion_prof", "bootcamp"],
    "construccion": ["construccion_residencial", "construccion_comercial", "obras_civiles", "remodelacion", "llave_en_mano", "demolicion", "estructuras_metalicas", "concreto_preparado", "materiales_petreos", "planos_3d"],
    "diseño": ["branding", "diseño_web_ux", "diseño_interiores", "packaging_diseño", "editorial", "consultoria_diseño", "manuales_marca", "assets_digitales", "prototipos_3d", "patrones_fichas", "ilustraciones"],
}


# =============================================================================
# FUNCIONES DE SEED
# =============================================================================
def seed_service_templates(db: Session) -> int:
    """Crea el catálogo de servicios. Idempotente."""
    from app.models import Category

    # Mapear category_code -> category_id
    categorias_map = {c.code: c for c in db.query(Category).all()}

    count = 0
    for data in SERVICE_TEMPLATES:
        existing = (
            db.query(ServiceTemplate)
            .filter(ServiceTemplate.code == data["code"])
            .first()
        )
        if not existing:
            category_code = data.pop("category_code", None)
            category = categorias_map.get(category_code) if category_code else None

            db.add(
                ServiceTemplate(
                    code=data["code"],
                    name=data["name"],
                    description=data["description"],
                    category_id=category.id if category else None,
                )
            )
            count += 1
            data["category_code"] = category_code  # restaurar para idempotencia
    db.commit()
    return count


def seed_verticals_services(db: Session) -> int:
    """Crea las relaciones N:M entre verticales y servicios. Idempotente."""
    count = 0

    verticales_map = {v.code: v for v in db.query(Vertical).all()}
    servicios_map = {s.code: s for s in db.query(ServiceTemplate).all()}

    for vertical_code, service_codes in VERTICAL_SERVICES.items():
        vertical = verticales_map.get(vertical_code)
        if not vertical:
            print(f"  Advertencia: Vertical no encontrado: {vertical_code}")
            continue

        for i, service_code in enumerate(service_codes):
            service = servicios_map.get(service_code)
            if not service:
                print(f"  Advertencia: Servicio no encontrado: {service_code} (para {vertical_code})")
                continue

            existing_rel = (
                db.query(VerticalService)
                .filter(
                    VerticalService.vertical_id == vertical.id,
                    VerticalService.service_id == service.id,
                )
                .first()
            )
            if not existing_rel:
                db.add(
                    VerticalService(
                        vertical_id=vertical.id,
                        service_id=service.id,
                        display_order=i + 1,
                    )
                )
                count += 1
    db.commit()
    return count