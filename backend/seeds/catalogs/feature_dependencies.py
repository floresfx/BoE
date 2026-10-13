"""Seed de dependencias entre features."""

from sqlalchemy.orm import Session

from app.models import Feature, FeatureDependency


DEPENDENCIES = [
    ("ia_completa", "ia_basica"),
    ("costeo_completo", "costeo_basico"),
    ("matching_inverso", "inventario"),
    ("matching_inverso", "planificacion"),
    ("prediccion_demanda", "inventario"),
    ("prediccion_mermas", "inventario"),
    ("multi_bodega", "inventario"),
]


def seed_feature_dependencies(db: Session) -> int:
    """Crea las dependencias entre features. Idempotente."""
    count = 0

    features = {f.code: f for f in db.query(Feature).all()}

    for feature_code, depends_code in DEPENDENCIES:
        feature = features.get(feature_code)
        depends_on = features.get(depends_code)

        if not feature or not depends_on:
            raise ValueError(
                f"No encontrado: {feature_code} -> {depends_code}"
            )

        existing = (
            db.query(FeatureDependency)
            .filter(
                FeatureDependency.feature_id == feature.id,
                FeatureDependency.depends_on_id == depends_on.id,
            )
            .first()
        )
        if existing:
            continue

        db.add(
            FeatureDependency(
                feature_id=feature.id,
                depends_on_id=depends_on.id,
            )
        )
        count += 1

    db.commit()
    return count