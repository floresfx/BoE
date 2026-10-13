"""Seed de ciudades.

Resuelve country_code y state_code.
"""

from sqlalchemy.orm import Session

from app.models import City, Country, State


CITIES = [
    # Venezuela
    ("VE", "DC", "Caracas"),
    ("VE", "MI", "Petare"),
    ("VE", "MI", "Baruta"),
    ("VE", "MI", "Chacao"),
    ("VE", "ZU", "Maracaibo"),
    ("VE", "ZU", "Cabimas"),
    ("VE", "ZU", "Ciudad Ojeda"),
    ("VE", "CA", "Valencia"),
    ("VE", "CA", "Naguanagua"),
    ("VE", "AR", "Maracay"),
    # Colombia
    ("CO", "ANT", "Medellin"),
    ("CO", "ANT", "Bello"),
    ("CO", "ANT", "Envigado"),
    ("CO", "CUN", "Bogota"),
    ("CO", "CUN", "Soacha"),
    ("CO", "CUN", "Chia"),
    ("CO", "VAC", "Cali"),
    ("CO", "VAC", "Palmira"),
    ("CO", "ATL", "Barranquilla"),
    ("CO", "BOL", "Cartagena"),
    # Panama
    ("PA", "8", "Ciudad de Panama"),
    ("PA", "8", "San Miguelito"),
    ("PA", "8", "Tocumen"),
    # Chile
    ("CL", "RM", "Santiago"),
    ("CL", "RM", "Puente Alto"),
    ("CL", "RM", "Maipu"),
    ("CL", "VS", "Valparaiso"),
    ("CL", "VS", "Vina del Mar"),
    ("CL", "BI", "Concepcion"),
    # Peru
    ("PE", "LIM", "Lima"),
    ("PE", "LIM", "Callao"),
    ("PE", "AQP", "Arequipa"),
    ("PE", "CUS", "Cusco"),
    # Ecuador
    ("EC", "P", "Quito"),
    ("EC", "P", "Sangolqui"),
    ("EC", "G", "Guayaquil"),
    ("EC", "G", "Samborondon"),
    ("EC", "A", "Cuenca"),
    # Mexico
    ("MX", "CDMX", "Ciudad de Mexico"),
    ("MX", "JAL", "Guadalajara"),
    ("MX", "JAL", "Zapopan"),
    ("MX", "NL", "Monterrey"),
    ("MX", "NL", "San Pedro Garza Garcia"),
    # Argentina
    ("AR", "CABA", "Buenos Aires"),
    ("AR", "BA", "La Plata"),
    ("AR", "BA", "Mar del Plata"),
    ("AR", "COR", "Cordoba"),
    # Espana
    ("ES", "MD", "Madrid"),
    ("ES", "MD", "Alcala de Henares"),
    ("ES", "CT", "Barcelona"),
    ("ES", "CT", "Badalona"),
    ("ES", "AN", "Sevilla"),
    ("ES", "AN", "Malaga"),
    # Estados Unidos
    ("US", "NY", "Nueva York"),
    ("US", "NY", "Buffalo"),
    ("US", "CA", "Los Angeles"),
    ("US", "CA", "San Francisco"),
    ("US", "TX", "Houston"),
    ("US", "TX", "Dallas"),
    ("US", "FL", "Miami"),
    ("US", "FL", "Orlando"),
]


def seed_cities(db: Session) -> int:
    """Crea las ciudades iniciales. Idempotente."""
    count = 0

    countries = {c.code: c for c in db.query(Country).all()}
    states = {
        (s.country_id, s.code): s
        for s in db.query(State).all()
    }

    for country_code, state_code, city_name in CITIES:
        country = countries.get(country_code)
        if not country:
            raise ValueError(f"Pais no encontrado: {country_code}")

        state = states.get((country.id, state_code))
        if not state:
            raise ValueError(
                f"Estado no encontrado: {country_code}/{state_code}"
            )

        existing = (
            db.query(City)
            .filter(
                City.country_id == country.id,
                City.state_id == state.id,
                City.name == city_name,
            )
            .first()
        )
        if existing:
            continue

        db.add(
            City(
                country_id=country.id,
                state_id=state.id,
                name=city_name,
            )
        )
        count += 1

    db.commit()
    return count