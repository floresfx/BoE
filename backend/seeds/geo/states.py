"""Seed de estados.

Resuelve country_code -> country_id.
"""

from sqlalchemy.orm import Session

from app.models import Country, State


STATES = [
    # Venezuela
    ("VE", "DC", "Distrito Capital"),
    ("VE", "MI", "Miranda"),
    ("VE", "ZU", "Zulia"),
    ("VE", "CA", "Carabobo"),
    ("VE", "AR", "Aragua"),
    # Colombia
    ("CO", "ANT", "Antioquia"),
    ("CO", "CUN", "Cundinamarca"),
    ("CO", "VAC", "Valle del Cauca"),
    ("CO", "ATL", "Atlantico"),
    ("CO", "BOL", "Bolivar"),
    # Panama
    ("PA", "8", "Panama"),
    ("PA", "9", "Veraguas"),
    ("PA", "10", "Los Santos"),
    # Chile
    ("CL", "RM", "Region Metropolitana"),
    ("CL", "VS", "Valparaiso"),
    ("CL", "BI", "Biobio"),
    # Peru
    ("PE", "LIM", "Lima"),
    ("PE", "AQP", "Arequipa"),
    ("PE", "CUS", "Cusco"),
    # Ecuador
    ("EC", "P", "Pichincha"),
    ("EC", "G", "Guayas"),
    ("EC", "A", "Azuay"),
    # Mexico
    ("MX", "CDMX", "Ciudad de Mexico"),
    ("MX", "JAL", "Jalisco"),
    ("MX", "NL", "Nuevo Leon"),
    # Argentina
    ("AR", "CABA", "Ciudad Autonoma de Buenos Aires"),
    ("AR", "BA", "Buenos Aires"),
    ("AR", "COR", "Cordoba"),
    # Espana
    ("ES", "MD", "Madrid"),
    ("ES", "CT", "Cataluna"),
    ("ES", "AN", "Andalucia"),
    # Estados Unidos
    ("US", "NY", "Nueva York"),
    ("US", "CA", "California"),
    ("US", "TX", "Texas"),
    ("US", "FL", "Florida"),
]


def seed_states(db: Session) -> int:
    """Crea los estados iniciales. Idempotente."""
    count = 0

    countries = {c.code: c for c in db.query(Country).all()}

    for country_code, state_code, name in STATES:
        country = countries.get(country_code)
        if not country:
            raise ValueError(f"Pais no encontrado: {country_code}")

        existing = (
            db.query(State)
            .filter(
                State.country_id == country.id,
                State.code == state_code,
            )
            .first()
        )
        if existing:
            continue

        db.add(
            State(
                country_id=country.id,
                code=state_code,
                name=name,
            )
        )
        count += 1

    db.commit()
    return count