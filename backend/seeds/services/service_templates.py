"""Seed de servicios operativos (service_templates).

Resuelve category_code -> category_id.
"""

from sqlalchemy.orm import Session

from app.models import Category, ServiceTemplate


SERVICES = [
    # Clinicas generales
    {"code": "consulta_medica", "name": "Consulta medica", "description": "Evaluacion inicial, recetas y control", "category_code": "salud"},
    {"code": "consulta_especialidad", "name": "Consulta de especialidad", "description": "Pediatria, ginecologia, cardiologia, dermatologia", "category_code": "salud"},
    {"code": "laboratorio_clinico", "name": "Laboratorio clinico", "description": "Analisis de sangre, orina y fluidos", "category_code": "salud"},
    {"code": "imagenologia", "name": "Imagenologia", "description": "Radiografias, ecografias, TAC, resonancias", "category_code": "salud"},
    {"code": "urgencias", "name": "Atencion de urgencias", "description": "Primeros auxilios y estabilizacion", "category_code": "salud"},
    {"code": "observacion", "name": "Unidad de observacion", "description": "Monitoreo por horas", "category_code": "salud"},
    {"code": "cirugia_ambulatoria", "name": "Cirugia ambulatoria", "description": "Operaciones sin hospitalizacion", "category_code": "salud"},
    {"code": "vacunacion", "name": "Vacunacion", "description": "Vacunas preventivas", "category_code": "salud"},
    {"code": "rehabilitacion", "name": "Rehabilitacion y terapias", "description": "Fisioterapia, terapia respiratoria", "category_code": "salud"},
    {"code": "chequeo_preventivo", "name": "Chequeos preventivos", "description": "Evaluaciones medicas de rutina", "category_code": "salud"},
    # Clinicas dentales
    {"code": "odontologia_general", "name": "Odontologia general", "description": "Revisiones, limpiezas, empastes", "category_code": "salud"},
    {"code": "ortodoncia", "name": "Ortodoncia", "description": "Brackets, alineadores", "category_code": "salud"},
    {"code": "implantologia", "name": "Implantologia", "description": "Implantes de titanio", "category_code": "salud"},
    {"code": "protesis_dental", "name": "Protesis dentales", "description": "Coronas, puentes, dentaduras", "category_code": "salud"},
    {"code": "estetica_dental", "name": "Estetica dental", "description": "Blanqueamientos, carillas", "category_code": "salud"},
    {"code": "endodoncia", "name": "Endodoncia", "description": "Tratamiento de nervio", "category_code": "salud"},
    {"code": "periodoncia", "name": "Periodoncia", "description": "Tratamiento de encias", "category_code": "salud"},
    {"code": "odontopediatria", "name": "Odontopediatria", "description": "Odontologia infantil", "category_code": "salud"},
    {"code": "cirugia_oral", "name": "Cirugia oral", "description": "Extracciones complejas", "category_code": "salud"},
    {"code": "radiologia_dental", "name": "Radiologia dental", "description": "Radiografias dentales", "category_code": "salud"},
    # Panaderias
    {"code": "panes_artesanales", "name": "Panes tradicionales y artesanales", "description": "Baguette, masa madre, pan campesino", "category_code": "comida"},
    {"code": "panes_especiales", "name": "Panes especiales y de molde", "description": "Integral, centeno, sin gluten, dulces", "category_code": "comida"},
    {"code": "bolleria", "name": "Bolleria y panaderia dulce", "description": "Croissants, berlinas, donuts, muffins", "category_code": "comida"},
    {"code": "pasteleria", "name": "Pasteleria y reposteria", "description": "Tartas, pasteles, bizcochos, galletas", "category_code": "comida"},
    {"code": "productos_salados", "name": "Productos salados horneados", "description": "Empanadas, quiches, pizzas, hojaldres", "category_code": "comida"},
    # Restaurantes
    {"code": "platos_carta", "name": "Platos a la carta", "description": "Entradas, platos fuertes, guarniciones", "category_code": "comida"},
    {"code": "bebidas_cocteleria", "name": "Bebidas y cocteleria", "description": "Jugos, cafes, cocteles, vinos", "category_code": "comida"},
    {"code": "menu_dia", "name": "Menus del dia o ejecutivos", "description": "Entrada, plato, bebida, postre", "category_code": "comida"},
    {"code": "reposteria_postres", "name": "Reposteria y postres caseros", "description": "Dulces, tartas, helados", "category_code": "comida"},
    {"code": "productos_gourmet", "name": "Productos gourmet", "description": "Salsas, aderezos, aceites, envasados", "category_code": "comida"},
    # Fabricantes
    {"code": "bienes_consumo_final", "name": "Bienes de consumo final", "description": "Alimentos empacados, ropa, electrodomesticos", "category_code": "otros"},
    {"code": "bienes_intermedios", "name": "Bienes intermedios", "description": "Chips, laminas de acero, piezas", "category_code": "otros"},
    {"code": "materias_primas_procesadas", "name": "Materias primas procesadas", "description": "Cemento, harinas, combustibles", "category_code": "otros"},
    {"code": "maquinaria_equipo", "name": "Maquinaria y bienes de equipo", "description": "Tractores, prensas, brazos roboticos", "category_code": "otros"},
    {"code": "embalajes_envases", "name": "Embalajes y envases", "description": "Cajas, botellas, latas, frascos", "category_code": "otros"},
    {"code": "maquila", "name": "Fabricacion por contrato", "description": "Produccion para marca externa", "category_code": "otros"},
    {"code": "marca_blanca", "name": "Produccion de marca blanca", "description": "Productos genericos con marca del cliente", "category_code": "otros"},
    {"code": "corte_mecanizado", "name": "Corte y mecanizado a la medida", "description": "Laser, CNC, chorro de agua", "category_code": "otros"},
    {"code": "copacking", "name": "Envasado y empaquetado externo", "description": "Dosificacion y empaque", "category_code": "otros"},
    {"code": "prototipos", "name": "Diseno y desarrollo de prototipos", "description": "Modelos fisicos o moldes", "category_code": "otros"},
    # Instituciones educativas
    {"code": "programas_academicos", "name": "Programas academicos y docencia", "description": "Clases teoricas y practicas con titulo", "category_code": "educacion"},
    {"code": "educacion_continua", "name": "Educacion continua y cursos libres", "description": "Talleres, diplomados, cursos cortos", "category_code": "educacion"},
    {"code": "tutorias", "name": "Tutorias y orientacion academica", "description": "Asesorias personalizadas o grupales", "category_code": "educacion"},
    {"code": "orientacion_psicologica", "name": "Orientacion psicologica", "description": "Apoyo profesional a alumnos", "category_code": "educacion"},
    {"code": "bolsa_trabajo", "name": "Bolsa de trabajo y practicas", "description": "Vinculacion con empresas", "category_code": "educacion"},
    {"code": "actividades_extracurriculares", "name": "Actividades extracurriculares", "description": "Deportes, artes, clubes", "category_code": "educacion"},
    {"code": "certificaciones", "name": "Certificaciones y titulos", "description": "Diplomas, actas con validez legal", "category_code": "educacion"},
    {"code": "plataforma_lms", "name": "Plataformas de aprendizaje virtual", "description": "Aulas digitales, contenidos, tareas", "category_code": "educacion"},
    {"code": "merchandising_edu", "name": "Articulos de identidad institucional", "description": "Uniformes, cuadernos, papelería", "category_code": "educacion"},
    # Proyectos por encargo
    {"code": "planificacion_eventos", "name": "Planificacion y coordinacion", "description": "Gestion del proyecto completo", "category_code": "otros"},
    {"code": "diseno_evento", "name": "Diseno y conceptualizacion", "description": "Identidad visual, tematica", "category_code": "otros"},
    {"code": "gestion_proveedores", "name": "Gestion de proveedores", "description": "Venue sourcing, catering, fotografia", "category_code": "otros"},
    {"code": "secretaria_tecnica", "name": "Secretaria tecnica y registro", "description": "RSVP, venta de entradas, acreditacion", "category_code": "otros"},
    {"code": "produccion_audiovisual", "name": "Produccion tecnica y audiovisual", "description": "Sonido, iluminacion, streaming", "category_code": "otros"},
    {"code": "protocolo_rrpp", "name": "Protocolo y relaciones publicas", "description": "Agenda, VIPs, prensa", "category_code": "otros"},
    {"code": "stands_escenografia", "name": "Diseno y construccion de stands", "description": "Estructuras personalizadas", "category_code": "otros"},
    {"code": "ambientacion_floral", "name": "Ambientacion y decoracion floral", "description": "Centros de mesa, altares, ramos", "category_code": "otros"},
    {"code": "papeleria_fina", "name": "Papeleria fina y carteleria", "description": "Invitaciones, minutas, senaletica", "category_code": "otros"},
    {"code": "material_promocional", "name": "Material promocional", "description": "Kits de bienvenida, recuerdos", "category_code": "otros"},
    {"code": "contenido_post_evento", "name": "Contenido audiovisual post-evento", "description": "Fotografias, videos, memorias", "category_code": "otros"},
    # Empresas de limpieza
    {"code": "limpieza_mantenimiento", "name": "Limpieza de mantenimiento", "description": "Servicio periodico (diario/semanal)", "category_code": "servicios"},
    {"code": "limpieza_profunda", "name": "Limpieza profunda", "description": "Intervencion exhaustiva", "category_code": "servicios"},
    {"code": "desinfeccion", "name": "Desinfeccion y sanitizacion", "description": "Productos grado hospitalario", "category_code": "servicios"},
    {"code": "limpieza_cristales", "name": "Limpieza de cristales y fachadas", "description": "Ventanas, mamparas, vidrios", "category_code": "servicios"},
    {"code": "tratamiento_suelos", "name": "Tratamiento y abrillantado de suelos", "description": "Decapado, pulido, encerado", "category_code": "servicios"},
    {"code": "lavado_tapiceria", "name": "Lavado de alfombras y tapizados", "description": "Alfombras, sillas, sillones, colchones", "category_code": "servicios"},
    {"code": "quimicos_limpieza", "name": "Quimicos de limpieza", "description": "Detergentes, desengrasantes, desinfectantes", "category_code": "servicios"},
    {"code": "utiles_limpieza", "name": "Utiles y herramientas de limpieza", "description": "Mopas, escobas, panos, carros", "category_code": "servicios"},
    {"code": "consumibles_higienicos", "name": "Consumibles higienicos", "description": "Papel higienico, toallas, jabon", "category_code": "servicios"},
    {"code": "dispensadores", "name": "Dispensadores y dosificadores", "description": "Jabon, gel, papel, ambientadores", "category_code": "servicios"},
    {"code": "maquinaria_limpieza", "name": "Maquinaria industrial de limpieza", "description": "Aspiradoras, hidrolimpiadoras, barredoras", "category_code": "servicios"},
    # Empresas de mantenimiento
    {"code": "mant_edilicio", "name": "Mantenimiento edilicio", "description": "Pintura, albanileria, plomeria, techos", "category_code": "servicios"},
    {"code": "mant_electrico", "name": "Mantenimiento electrico", "description": "Tableros, cableado, luminarias", "category_code": "servicios"},
    {"code": "mant_hvac", "name": "Mantenimiento de climatizacion", "description": "Aire acondicionado, calefaccion, ventilacion", "category_code": "servicios"},
    {"code": "mant_mecanico", "name": "Mantenimiento mecanico industrial", "description": "Maquinaria, motores, bandas", "category_code": "servicios"},
    {"code": "mant_seguridad", "name": "Mantenimiento de seguridad", "description": "CCTV, alarmas, extintores", "category_code": "servicios"},
    {"code": "mant_preventivo", "name": "Mantenimiento preventivo programado", "description": "Visitas periodicas con checklist", "category_code": "servicios"},
    {"code": "repuestos", "name": "Piezas de repuesto y consumibles", "description": "Filtros, bujias, correas, valvulas", "category_code": "servicios"},
    {"code": "herramientas_industriales", "name": "Herramientas y ferreteria industrial", "description": "Manuales, electricas, neumaticas", "category_code": "servicios"},
    {"code": "lubricantes", "name": "Lubricantes y quimicos tecnicos", "description": "Aceites, grasas, refrigerantes", "category_code": "servicios"},
    {"code": "materiales_fijacion", "name": "Materiales de fijacion", "description": "Tornillos, pernos, anclajes, siliconas", "category_code": "servicios"},
    {"code": "epp", "name": "Equipos e insumos de seguridad (EPP)", "description": "Cascos, guantes, calzado, arneses", "category_code": "servicios"},
    # Empresas de transporte
    {"code": "carga_local", "name": "Transporte de carga local", "description": "Envio por via terrestre local", "category_code": "servicios"},
    {"code": "carga_nacional", "name": "Transporte de carga nacional", "description": "Envio terrestre nacional", "category_code": "servicios"},
    {"code": "carga_internacional", "name": "Transporte de carga internacional", "description": "Terrestre, maritimo, aereo", "category_code": "servicios"},
    {"code": "carga_especial", "name": "Transporte de carga especial", "description": "Maquinaria pesada, estructuras", "category_code": "servicios"},
    {"code": "paqueteria", "name": "Paqueteria y mensajeria express", "description": "Sobres, documentos, paquetes", "category_code": "servicios"},
    {"code": "carga_pesada", "name": "Transporte de carga pesada", "description": "Plataformas especializadas", "category_code": "servicios"},
    {"code": "transporte_refrigerado", "name": "Transporte refrigerado", "description": "Perecederos, medicinas, quimicos", "category_code": "servicios"},
    {"code": "almacenaje", "name": "Almacenaje y gestion de inventarios", "description": "Bodegas logisticas", "category_code": "servicios"},
    {"code": "transporte_pasajeros", "name": "Transporte de pasajeros", "description": "Publico, corporativo, escolar, turistico", "category_code": "servicios"},
    {"code": "embalajes_proteccion", "name": "Embalajes y materiales de proteccion", "description": "Cajas, palés, burbujas, cintas", "category_code": "servicios"},
    {"code": "contenedores", "name": "Venta o alquiler de contenedores", "description": "Contenedores 20/40 pies, reefers", "category_code": "servicios"},
    {"code": "gps_rastreo", "name": "Sistemas y software de rastreo (GPS)", "description": "Dispositivos y plataformas", "category_code": "servicios"},
    {"code": "flotas_usadas", "name": "Flotas vehiculares usadas o repuestos", "description": "Camiones, furgonetas, componentes", "category_code": "servicios"},
    # Hoteles
    {"code": "estadia_estandar", "name": "Estadia estandar", "description": "Habitacion estandar con servicios basicos", "category_code": "servicios"},
    {"code": "estadia_suite", "name": "Estadia en suite", "description": "Habitacion premium con amenities", "category_code": "servicios"},
    {"code": "paquete_turistico", "name": "Paquete turistico", "description": "Alojamiento + actividades", "category_code": "servicios"},
    {"code": "eventos_hotel", "name": "Eventos y conferencias", "description": "Salones, catering, audiovisual", "category_code": "servicios"},
    {"code": "restaurante_hotel", "name": "Restaurante y bar", "description": "Comidas y bebidas en el hotel", "category_code": "servicios"},
    # Heladerias
    {"code": "helado_artesanal", "name": "Helados artesanales", "description": "Conos, vasos, tarrinas", "category_code": "comida"},
    {"code": "gelato", "name": "Gelato italiano", "description": "Textura densa, menos grasa", "category_code": "comida"},
    {"code": "soft_serve", "name": "Helado suave (Soft Serve)", "description": "Maquina de palanca", "category_code": "comida"},
    {"code": "frozen_yogurt", "name": "Yogur helado", "description": "Base de yogur, con toppings", "category_code": "comida"},
    {"code": "paletas", "name": "Paletas o polos", "description": "Helados con palito", "category_code": "comida"},
    {"code": "malteadas", "name": "Malteadas y batidos", "description": "Bebidas frias con helado", "category_code": "comida"},
    {"code": "postres_helados", "name": "Pasteles y postres helados", "description": "Tortas, Banana Split, copas", "category_code": "comida"},
    {"code": "toppings", "name": "Toppings y coberturas", "description": "Frutas, frutos secos, siropes", "category_code": "comida"},
    # Talleres
    {"code": "mant_auto_preventivo", "name": "Mantenimiento preventivo", "description": "Aceite, filtros, revision de niveles", "category_code": "servicios"},
    {"code": "diagnostico_auto", "name": "Diagnostico por computadora", "description": "Escaneo electronico", "category_code": "servicios"},
    {"code": "reparacion_frenos", "name": "Reparacion de frenos", "description": "Discos, balatas, liquido", "category_code": "servicios"},
    {"code": "suspension_direccion", "name": "Suspension y direccion", "description": "Amortiguadores, alineacion, balanceo", "category_code": "servicios"},
    {"code": "reparacion_motor", "name": "Reparacion de motor", "description": "Bandas, empaques, cajas", "category_code": "servicios"},
    {"code": "electricidad_auto", "name": "Electricidad automotriz", "description": "Marcha, alternador, baterias", "category_code": "servicios"},
    {"code": "aire_acondicionado_auto", "name": "Aire acondicionado automotriz", "description": "Recarga de gas, compresores", "category_code": "servicios"},
    {"code": "hojalateria_pintura", "name": "Hojalateria y pintura", "description": "Abolladuras, pintura automotriz", "category_code": "servicios"},
    {"code": "refacciones_auto", "name": "Refacciones y componentes", "description": "Bujias, balatas, filtros, bombas", "category_code": "servicios"},
    {"code": "llantas", "name": "Llantas y neumaticos", "description": "Marcas, medidas, rangos", "category_code": "servicios"},
    {"code": "baterias_auto", "name": "Baterias automotrices", "description": "Acumuladores", "category_code": "servicios"},
    {"code": "fluidos_auto", "name": "Fluidos y lubricantes", "description": "Aceites, frenos, refrigerantes", "category_code": "servicios"},
    {"code": "accesorios_auto", "name": "Accesorios y consumibles", "description": "Plumillas, focos, fusibles", "category_code": "servicios"},
    # Ferreterias
    {"code": "ferreteria_general", "name": "Ferreteria general", "description": "Herramientas, materiales, tornilleria", "category_code": "otros"},
    {"code": "materiales_construccion", "name": "Materiales de construccion", "description": "Cemento, cabillas, bloques, arena", "category_code": "construccion"},
    {"code": "pintura_ferreteria", "name": "Pintura y acabados", "description": "Pinturas, barnices, solventes", "category_code": "construccion"},
    {"code": "plomeria_ferreteria", "name": "Plomeria y griferia", "description": "Tuberias, conexiones, llaves", "category_code": "construccion"},
    {"code": "electricidad_ferreteria", "name": "Electricidad y cableado", "description": "Cables, breakers, tomacorrientes", "category_code": "construccion"},
    {"code": "herramientas_manuales", "name": "Herramientas manuales", "description": "Martillos, destornilladores, llaves", "category_code": "otros"},
    {"code": "herramientas_electricas", "name": "Herramientas electricas", "description": "Taladros, sierras, esmeriles", "category_code": "otros"},
    {"code": "jardin_ferreteria", "name": "Jardin y exterior", "description": "Mangueras, cortadoras, semillas", "category_code": "otros"},
    # Distribuidoras
    {"code": "consumo_masivo", "name": "Bienes de consumo masivo", "description": "Alimentos, bebidas, limpieza, aseo", "category_code": "otros"},
    {"code": "farmaceuticos", "name": "Productos farmaceuticos y medicos", "description": "Medicamentos, material de curacion", "category_code": "salud"},
    {"code": "construccion_mayorista", "name": "Materiales de construccion mayorista", "description": "Mayoreo para tiendas y constructoras", "category_code": "construccion"},
    {"code": "tecnologia_mayorista", "name": "Componentes tecnologicos", "description": "Computacion, moviles, electrodomesticos", "category_code": "tecnologia"},
    {"code": "suministros_industriales", "name": "Suministros industriales", "description": "Quimicos, lubricantes, envases", "category_code": "otros"},
    # Laboratorios
    {"code": "analisis_clinicos", "name": "Analisis clinicos y de salud", "description": "Sangre, orina, tejidos, ADN", "category_code": "salud"},
    {"code": "pruebas_microbiologicas", "name": "Pruebas microbiologicas", "description": "Bacterias, hongos, virus", "category_code": "salud"},
    {"code": "control_calidad", "name": "Control de calidad industrial", "description": "Resistencia, pureza, composicion", "category_code": "otros"},
    {"code": "analisis_ambientales", "name": "Analisis ambientales", "description": "Agua, aire, suelos", "category_code": "otros"},
    {"code": "estabilidad_caducidad", "name": "Estudios de estabilidad y caducidad", "description": "Temperatura y humedad controladas", "category_code": "otros"},
    {"code": "calibracion_equipos", "name": "Calibracion de equipos", "description": "Balanzas, termometros, manometros", "category_code": "otros"},
    {"code": "fabricacion_farma", "name": "Medicamentos y formulas", "description": "Farmacos, jarabes, vacunas", "category_code": "salud"},
    {"code": "reactivos_quimicos", "name": "Reactivos quimicos", "description": "Compuestos para analisis", "category_code": "otros"},
    {"code": "kits_diagnostico", "name": "Kits de diagnostico rapido", "description": "Embarazo, glucosa, antigenos", "category_code": "salud"},
    {"code": "medios_cultivo", "name": "Medios de cultivo", "description": "Agar, preparados nutritivos", "category_code": "otros"},
    {"code": "materiales_referencia", "name": "Materiales de referencia", "description": "Muestras de pureza conocida", "category_code": "otros"},
    # Academias
    {"code": "curso_corto", "name": "Curso corto", "description": "Formacion especifica de horas", "category_code": "educacion"},
    {"code": "taller_intensivo", "name": "Taller intensivo", "description": "Formacion practica concentrada", "category_code": "educacion"},
    {"code": "clase_magistral", "name": "Clase magistral", "description": "Sesion con experto", "category_code": "educacion"},
    {"code": "certificacion_prof", "name": "Certificacion profesional", "description": "Acredita competencias", "category_code": "educacion"},
    {"code": "bootcamp", "name": "Bootcamp", "description": "Formacion intensiva inmersiva", "category_code": "educacion"},
    # Construccion
    {"code": "construccion_residencial", "name": "Construccion residencial", "description": "Viviendas, conjuntos, edificios", "category_code": "construccion"},
    {"code": "construccion_comercial", "name": "Construccion comercial", "description": "Oficinas, centros comerciales, naves", "category_code": "construccion"},
    {"code": "obras_civiles", "name": "Obras civiles e infraestructura", "description": "Carreteras, puentes, represas", "category_code": "construccion"},
    {"code": "remodelacion", "name": "Remodelacion y ampliacion", "description": "Modificacion de estructuras", "category_code": "construccion"},
    {"code": "llave_en_mano", "name": "Llave en mano", "description": "Planos + permisos + obra", "category_code": "construccion"},
    {"code": "demolicion", "name": "Demolicion y preparacion", "description": "Derribo, excavacion, nivelacion", "category_code": "construccion"},
    {"code": "estructuras_metalicas", "name": "Estructuras metalicas", "description": "Vigas, naves, paneles, modulos", "category_code": "construccion"},
    {"code": "concreto_preparado", "name": "Mezclas de concreto", "description": "Concreto fresco en camiones", "category_code": "construccion"},
    {"code": "materiales_petreos", "name": "Materiales petreos", "description": "Arena, grava, piedra, asfalto", "category_code": "construccion"},
    {"code": "planos_3d", "name": "Planos tecnicos y modelos 3D", "description": "Maquetas, BIM, disenos", "category_code": "construccion"},
    # Diseno
    {"code": "branding", "name": "Branding e identidad", "description": "Logo, paleta, tipografia, manual", "category_code": "otros"},
    {"code": "diseno_web_ux", "name": "Diseno web y UX/UI", "description": "Interfaz y experiencia", "category_code": "tecnologia"},
    {"code": "diseno_interiores", "name": "Diseno de interiores", "description": "Espacios fisicos, mobiliario", "category_code": "otros"},
    {"code": "packaging_diseno", "name": "Diseno de packaging", "description": "Envases, etiquetas, cajas", "category_code": "otros"},
    {"code": "editorial", "name": "Diseno editorial", "description": "Revistas, libros, catalogos", "category_code": "otros"},
    {"code": "consultoria_diseno", "name": "Consultoria de diseno", "description": "Asesoria estrategica", "category_code": "otros"},
    {"code": "manuales_marca", "name": "Manuales de marca", "description": "Documentos tecnicos de uso", "category_code": "otros"},
    {"code": "assets_digitales", "name": "Assets digitales y plantillas", "description": "Posts, presentaciones, banners", "category_code": "otros"},
    {"code": "prototipos_3d", "name": "Prototipos y maquetas en 3D", "description": "Modelos digitales o fisicos", "category_code": "otros"},
    {"code": "patrones_fichas", "name": "Patrones y fichas tecnicas", "description": "Planos, especificaciones", "category_code": "otros"},
    {"code": "ilustraciones", "name": "Ilustraciones y tipografias", "description": "Dibujos, fuentes, iconos", "category_code": "otros"},
]


def seed_service_templates(db: Session) -> int:
    """Crea los service templates iniciales. Idempotente."""
    count = 0
    categories = {c.code: c for c in db.query(Category).all()}

    for data in SERVICES:
        existing = (
            db.query(ServiceTemplate)
            .filter(ServiceTemplate.code == data["code"])
            .first()
        )
        if existing:
            continue

        category = categories.get(data["category_code"])
        if not category:
            raise ValueError(
                f"Categoria no encontrada: {data['category_code']}"
            )

        db.add(
            ServiceTemplate(
                code=data["code"],
                name=data["name"],
                description=data["description"],
                category_id=category.id,
            )
        )
        count += 1

    db.commit()
    return count