"""Endpoints del panel de administración del SaaS.

Todos los endpoints requieren rol SuperAdmin.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_superadmin
from app.core.database import get_db
from app.models import (
    Attribute,
    AttributeType,
    Category,
    Country,
    Currency,
    DocumentType,
    Feature,
    Plan,
    PlanFeature,
    PlanLimit,
    ServiceTemplate,
    Tax,
    Unit,
    User,
    Vertical,
)
from app.schemas.admin import (
    AttributeAdminCreate,
    AttributeAdminUpdate,
    CategoryAdminCreate,
    CategoryAdminUpdate,
    CountryAdminCreate,
    CountryAdminUpdate,
    CurrencyAdminCreate,
    CurrencyAdminUpdate,
    DocumentTypeAdminCreate,
    DocumentTypeAdminUpdate,
    FeatureAdminCreate,
    FeatureAdminUpdate,
    PlanAdminCreate,
    PlanAdminUpdate,
    ServiceTemplateAdminCreate,
    ServiceTemplateAdminUpdate,
    TaxAdminCreate,
    TaxAdminUpdate,
    UnitAdminCreate,
    UnitAdminUpdate,
    VerticalAdminCreate,
    VerticalAdminUpdate,
)

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_superadmin)],
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_or_404(db: Session, model, id_value: UUID, name: str):
    obj = db.query(model).filter(model.id == id_value).first()
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{name} no encontrado",
        )
    return obj


# ---------------------------------------------------------------------------
# Verticales
# ---------------------------------------------------------------------------

@router.get("/verticals")
def admin_list_verticals(db: Session = Depends(get_db)):
    """Lista todos los verticales (activos e inactivos)."""
    vs = db.query(Vertical).order_by(Vertical.name).all()
    return [
        {
            "id": str(v.id),
            "code": v.code,
            "name": v.name,
            "description": v.description,
            "is_active": v.is_active,
        }
        for v in vs
    ]


@router.post("/verticals", status_code=status.HTTP_201_CREATED)
def admin_create_vertical(
    data: VerticalAdminCreate, db: Session = Depends(get_db)
):
    existing = db.query(Vertical).filter(Vertical.code == data.code).first()
    if existing:
        raise HTTPException(400, "Ya existe un vertical con ese código")
    v = Vertical(**data.model_dump())
    db.add(v)
    db.commit()
    db.refresh(v)
    return {
        "id": str(v.id),
        "code": v.code,
        "name": v.name,
        "description": v.description,
        "is_active": v.is_active,
    }


@router.put("/verticals/{vertical_id}")
def admin_update_vertical(
    vertical_id: UUID,
    data: VerticalAdminUpdate,
    db: Session = Depends(get_db),
):
    v = _get_or_404(db, Vertical, vertical_id, "Vertical")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(v, key, value)
    db.commit()
    db.refresh(v)
    return {
        "id": str(v.id),
        "code": v.code,
        "name": v.name,
        "description": v.description,
        "is_active": v.is_active,
    }


# ---------------------------------------------------------------------------
# Features
# ---------------------------------------------------------------------------

@router.get("/features")
def admin_list_features(db: Session = Depends(get_db)):
    fs = db.query(Feature).order_by(Feature.name).all()
    return [
        {
            "id": str(f.id),
            "code": f.code,
            "name": f.name,
            "description": f.description,
            "applies_to": f.applies_to,
            "is_active": f.is_active,
        }
        for f in fs
    ]


@router.post("/features", status_code=status.HTTP_201_CREATED)
def admin_create_feature(
    data: FeatureAdminCreate, db: Session = Depends(get_db)
):
    existing = db.query(Feature).filter(Feature.code == data.code).first()
    if existing:
        raise HTTPException(400, "Ya existe una feature con ese código")
    f = Feature(**data.model_dump())
    db.add(f)
    db.commit()
    db.refresh(f)
    return {
        "id": str(f.id),
        "code": f.code,
        "name": f.name,
        "description": f.description,
        "applies_to": f.applies_to,
        "is_active": f.is_active,
    }


@router.put("/features/{feature_id}")
def admin_update_feature(
    feature_id: UUID,
    data: FeatureAdminUpdate,
    db: Session = Depends(get_db),
):
    f = _get_or_404(db, Feature, feature_id, "Feature")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(f, key, value)
    db.commit()
    db.refresh(f)
    return {
        "id": str(f.id),
        "code": f.code,
        "name": f.name,
        "description": f.description,
        "applies_to": f.applies_to,
        "is_active": f.is_active,
    }


# ---------------------------------------------------------------------------
# Planes
# ---------------------------------------------------------------------------

@router.get("/plans")
def admin_list_plans(db: Session = Depends(get_db)):
    plans = db.query(Plan).order_by(Plan.price).all()
    return [_plan_to_dict(db, p) for p in plans]


def _plan_to_dict(db: Session, plan: Plan) -> dict:
    features = [
        pf.feature.code
        for pf in db.query(PlanFeature).filter(PlanFeature.plan_id == plan.id).all()
        if pf.feature
    ]
    limits = {
        pl.limit_code: pl.value
        for pl in db.query(PlanLimit).filter(PlanLimit.plan_id == plan.id).all()
    }
    return {
        "id": str(plan.id),
        "code": plan.code,
        "name": plan.name,
        "price": str(plan.price),
        "currency_id": str(plan.currency_id),
        "interval": plan.interval,
        "trial_days": plan.trial_days,
        "is_active": plan.is_active,
        "feature_codes": features,
        "limits": limits,
    }


@router.post("/plans", status_code=status.HTTP_201_CREATED)
def admin_create_plan(data: PlanAdminCreate, db: Session = Depends(get_db)):
    existing = db.query(Plan).filter(Plan.code == data.code).first()
    if existing:
        raise HTTPException(400, "Ya existe un plan con ese código")

    plan_data = data.model_dump(exclude={"feature_codes", "limits"})
    plan = Plan(**plan_data)
    db.add(plan)
    db.flush()

    # Features
    for fcode in data.feature_codes:
        feature = db.query(Feature).filter(Feature.code == fcode).first()
        if feature:
            db.add(PlanFeature(plan_id=plan.id, feature_id=feature.id))

    # Limits
    for lcode, lvalue in data.limits.items():
        db.add(PlanLimit(plan_id=plan.id, limit_code=lcode, value=lvalue))

    db.commit()
    db.refresh(plan)
    return _plan_to_dict(db, plan)


@router.put("/plans/{plan_id}")
def admin_update_plan(
    plan_id: UUID,
    data: PlanAdminUpdate,
    db: Session = Depends(get_db),
):
    plan = _get_or_404(db, Plan, plan_id, "Plan")
    update_data = data.model_dump(
        exclude_unset=True, exclude={"feature_codes", "limits"}
    )
    for key, value in update_data.items():
        setattr(plan, key, value)

    if data.feature_codes is not None:
        db.query(PlanFeature).filter(PlanFeature.plan_id == plan.id).delete()
        for fcode in data.feature_codes:
            feature = db.query(Feature).filter(Feature.code == fcode).first()
            if feature:
                db.add(PlanFeature(plan_id=plan.id, feature_id=feature.id))

    if data.limits is not None:
        db.query(PlanLimit).filter(PlanLimit.plan_id == plan.id).delete()
        for lcode, lvalue in data.limits.items():
            db.add(PlanLimit(plan_id=plan.id, limit_code=lcode, value=lvalue))

    db.commit()
    db.refresh(plan)
    return _plan_to_dict(db, plan)


# ---------------------------------------------------------------------------
# Atributos
# ---------------------------------------------------------------------------

@router.get("/attributes")
def admin_list_attributes(db: Session = Depends(get_db)):
    attrs = db.query(Attribute).order_by(Attribute.name).all()
    types = {t.id: t.code for t in db.query(AttributeType).all()}
    return [
        {
            "id": str(a.id),
            "code": a.code,
            "name": a.name,
            "type_code": types.get(a.type_id, ""),
            "is_active": a.is_active,
        }
        for a in attrs
    ]


@router.post("/attributes", status_code=status.HTTP_201_CREATED)
def admin_create_attribute(
    data: AttributeAdminCreate, db: Session = Depends(get_db)
):
    existing = db.query(Attribute).filter(Attribute.code == data.code).first()
    if existing:
        raise HTTPException(400, "Ya existe un atributo con ese código")
    atype = (
        db.query(AttributeType).filter(AttributeType.code == data.type_code).first()
    )
    if not atype:
        raise HTTPException(400, f"Tipo de atributo no encontrado: {data.type_code}")

    a = Attribute(
        code=data.code,
        name=data.name,
        type_id=atype.id,
        is_active=data.is_active,
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return {
        "id": str(a.id),
        "code": a.code,
        "name": a.name,
        "type_code": atype.code,
        "is_active": a.is_active,
    }


@router.put("/attributes/{attribute_id}")
def admin_update_attribute(
    attribute_id: UUID,
    data: AttributeAdminUpdate,
    db: Session = Depends(get_db),
):
    a = _get_or_404(db, Attribute, attribute_id, "Atributo")
    update_data = data.model_dump(exclude_unset=True)
    if "type_code" in update_data:
        atype = (
            db.query(AttributeType)
            .filter(AttributeType.code == update_data.pop("type_code"))
            .first()
        )
        if not atype:
            raise HTTPException(400, "Tipo de atributo no encontrado")
        a.type_id = atype.id
    for key, value in update_data.items():
        setattr(a, key, value)
    db.commit()
    db.refresh(a)
    return {
        "id": str(a.id),
        "code": a.code,
        "name": a.name,
        "type_code": db.query(AttributeType).get(a.type_id).code,
        "is_active": a.is_active,
    }


# ---------------------------------------------------------------------------
# Impuestos
# ---------------------------------------------------------------------------

@router.get("/taxes")
def admin_list_taxes(db: Session = Depends(get_db)):
    taxes = db.query(Tax).order_by(Tax.name).all()
    countries = {c.id: c.code for c in db.query(Country).all()}
    return [
        {
            "id": str(t.id),
            "country_code": countries.get(t.country_id, ""),
            "code": t.code,
            "name": t.name,
            "rate": str(t.rate),
            "applies_to": t.applies_to,
            "is_active": t.is_active,
        }
        for t in taxes
    ]


@router.post("/taxes", status_code=status.HTTP_201_CREATED)
def admin_create_tax(data: TaxAdminCreate, db: Session = Depends(get_db)):
    country = (
        db.query(Country).filter(Country.code == data.country_code).first()
    )
    if not country:
        raise HTTPException(400, f"País no encontrado: {data.country_code}")
    existing = (
        db.query(Tax)
        .filter(Tax.country_id == country.id, Tax.code == data.code)
        .first()
    )
    if existing:
        raise HTTPException(400, "Ya existe un impuesto con ese código para ese país")

    t = Tax(
        country_id=country.id,
        code=data.code,
        name=data.name,
        rate=data.rate,
        applies_to=data.applies_to,
        is_active=data.is_active,
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return {
        "id": str(t.id),
        "country_code": country.code,
        "code": t.code,
        "name": t.name,
        "rate": str(t.rate),
        "applies_to": t.applies_to,
        "is_active": t.is_active,
    }


@router.put("/taxes/{tax_id}")
def admin_update_tax(
    tax_id: UUID,
    data: TaxAdminUpdate,
    db: Session = Depends(get_db),
):
    t = _get_or_404(db, Tax, tax_id, "Impuesto")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(t, key, value)
    db.commit()
    db.refresh(t)
    return {
        "id": str(t.id),
        "code": t.code,
        "name": t.name,
        "rate": str(t.rate),
        "applies_to": t.applies_to,
        "is_active": t.is_active,
    }


# ---------------------------------------------------------------------------
# Servicios
# ---------------------------------------------------------------------------

@router.get("/services")
def admin_list_services(db: Session = Depends(get_db)):
    services = db.query(ServiceTemplate).order_by(ServiceTemplate.name).all()
    return [
        {
            "id": str(s.id),
            "code": s.code,
            "name": s.name,
            "description": s.description,
            "category_id": str(s.category_id) if s.category_id else None,
            "is_active": s.is_active,
        }
        for s in services
    ]


@router.post("/services", status_code=status.HTTP_201_CREATED)
def admin_create_service(
    data: ServiceTemplateAdminCreate, db: Session = Depends(get_db)
):
    existing = (
        db.query(ServiceTemplate)
        .filter(ServiceTemplate.code == data.code)
        .first()
    )
    if existing:
        raise HTTPException(400, "Ya existe un servicio con ese código")
    s = ServiceTemplate(**data.model_dump())
    db.add(s)
    db.commit()
    db.refresh(s)
    return {
        "id": str(s.id),
        "code": s.code,
        "name": s.name,
        "description": s.description,
        "category_id": str(s.category_id) if s.category_id else None,
        "is_active": s.is_active,
    }


@router.put("/services/{service_id}")
def admin_update_service(
    service_id: UUID,
    data: ServiceTemplateAdminUpdate,
    db: Session = Depends(get_db),
):
    s = _get_or_404(db, ServiceTemplate, service_id, "Servicio")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(s, key, value)
    db.commit()
    db.refresh(s)
    return {
        "id": str(s.id),
        "code": s.code,
        "name": s.name,
        "description": s.description,
        "category_id": str(s.category_id) if s.category_id else None,
        "is_active": s.is_active,
    }


# ---------------------------------------------------------------------------
# CURRENCIES (Bloque 2)
# ---------------------------------------------------------------------------

@router.get("/currencies")
def admin_list_currencies(db: Session = Depends(get_db)):
    cs = db.query(Currency).order_by(Currency.code).all()
    return [
        {
            "id": str(c.id),
            "code": c.code,
            "name": c.name,
            "symbol": c.symbol,
            "decimals": c.decimals,
            "is_base": c.is_base,
            "is_active": c.is_active,
        }
        for c in cs
    ]


@router.post("/currencies", status_code=status.HTTP_201_CREATED)
def admin_create_currency(
    data: CurrencyAdminCreate, db: Session = Depends(get_db)
):
    existing = db.query(Currency).filter(Currency.code == data.code).first()
    if existing:
        raise HTTPException(400, "Ya existe una moneda con ese código")
    if data.is_base:
        db.query(Currency).filter(Currency.is_base.is_(True)).update(
            {"is_base": False}
        )
    c = Currency(**data.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return {
        "id": str(c.id),
        "code": c.code,
        "name": c.name,
        "symbol": c.symbol,
        "decimals": c.decimals,
        "is_base": c.is_base,
        "is_active": c.is_active,
    }


@router.put("/currencies/{currency_id}")
def admin_update_currency(
    currency_id: UUID,
    data: CurrencyAdminUpdate,
    db: Session = Depends(get_db),
):
    c = _get_or_404(db, Currency, currency_id, "Moneda")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(c, key, value)
    db.commit()
    db.refresh(c)
    return {
        "id": str(c.id),
        "code": c.code,
        "name": c.name,
        "symbol": c.symbol,
        "decimals": c.decimals,
        "is_base": c.is_base,
        "is_active": c.is_active,
    }


# ---------------------------------------------------------------------------
# UNITS (Bloque 2)
# ---------------------------------------------------------------------------

@router.get("/units")
def admin_list_units(db: Session = Depends(get_db)):
    units = db.query(Unit).order_by(Unit.name).all()
    return [
        {
            "id": str(u.id),
            "code": u.code,
            "name": u.name,
            "symbol": u.symbol,
            "category_id": str(u.category_id),
            "is_base": u.is_base,
            "is_active": u.is_active,
        }
        for u in units
    ]


@router.post("/units", status_code=status.HTTP_201_CREATED)
def admin_create_unit(data: UnitAdminCreate, db: Session = Depends(get_db)):
    existing = db.query(Unit).filter(Unit.code == data.code).first()
    if existing:
        raise HTTPException(400, "Ya existe una unidad con ese código")
    u = Unit(**data.model_dump())
    db.add(u)
    db.commit()
    db.refresh(u)
    return {
        "id": str(u.id),
        "code": u.code,
        "name": u.name,
        "symbol": u.symbol,
        "category_id": str(u.category_id),
        "is_base": u.is_base,
        "is_active": u.is_active,
    }


@router.put("/units/{unit_id}")
def admin_update_unit(
    unit_id: UUID,
    data: UnitAdminUpdate,
    db: Session = Depends(get_db),
):
    u = _get_or_404(db, Unit, unit_id, "Unidad")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(u, key, value)
    db.commit()
    db.refresh(u)
    return {
        "id": str(u.id),
        "code": u.code,
        "name": u.name,
        "symbol": u.symbol,
        "category_id": str(u.category_id),
        "is_base": u.is_base,
        "is_active": u.is_active,
    }


# ---------------------------------------------------------------------------
# CATEGORIES (Bloque 2)
# ---------------------------------------------------------------------------

@router.get("/categories")
def admin_list_categories(db: Session = Depends(get_db)):
    cs = db.query(Category).order_by(Category.name).all()
    return [
        {
            "id": str(c.id),
            "code": c.code,
            "name": c.name,
            "is_active": c.is_active,
        }
        for c in cs
    ]


@router.post("/categories", status_code=status.HTTP_201_CREATED)
def admin_create_category(
    data: CategoryAdminCreate, db: Session = Depends(get_db)
):
    existing = db.query(Category).filter(Category.code == data.code).first()
    if existing:
        raise HTTPException(400, "Ya existe una categoría con ese código")
    c = Category(**data.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return {
        "id": str(c.id),
        "code": c.code,
        "name": c.name,
        "is_active": c.is_active,
    }


@router.put("/categories/{category_id}")
def admin_update_category(
    category_id: UUID,
    data: CategoryAdminUpdate,
    db: Session = Depends(get_db),
):
    c = _get_or_404(db, Category, category_id, "Categoría")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(c, key, value)
    db.commit()
    db.refresh(c)
    return {
        "id": str(c.id),
        "code": c.code,
        "name": c.name,
        "is_active": c.is_active,
    }


# ---------------------------------------------------------------------------
# COUNTRIES (Bloque 2)
# ---------------------------------------------------------------------------

@router.get("/countries")
def admin_list_countries(db: Session = Depends(get_db)):
    cs = db.query(Country).order_by(Country.name).all()
    return [
        {
            "id": str(c.id),
            "code": c.code,
            "name": c.name,
            "timezone_id": str(c.timezone_id),
            "currency_id": str(c.currency_id),
            "phone_prefix": c.phone_prefix,
            "is_active": c.is_active,
        }
        for c in cs
    ]


@router.post("/countries", status_code=status.HTTP_201_CREATED)
def admin_create_country(
    data: CountryAdminCreate, db: Session = Depends(get_db)
):
    existing = db.query(Country).filter(Country.code == data.code).first()
    if existing:
        raise HTTPException(400, "Ya existe un país con ese código")
    c = Country(**data.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return {
        "id": str(c.id),
        "code": c.code,
        "name": c.name,
        "timezone_id": str(c.timezone_id),
        "currency_id": str(c.currency_id),
        "phone_prefix": c.phone_prefix,
        "is_active": c.is_active,
    }


@router.put("/countries/{country_id}")
def admin_update_country(
    country_id: UUID,
    data: CountryAdminUpdate,
    db: Session = Depends(get_db),
):
    c = _get_or_404(db, Country, country_id, "País")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(c, key, value)
    db.commit()
    db.refresh(c)
    return {
        "id": str(c.id),
        "code": c.code,
        "name": c.name,
        "timezone_id": str(c.timezone_id),
        "currency_id": str(c.currency_id),
        "phone_prefix": c.phone_prefix,
        "is_active": c.is_active,
    }


# ---------------------------------------------------------------------------
# DOCUMENT TYPES (Bloque 2)
# ---------------------------------------------------------------------------

@router.get("/document-types")
def admin_list_document_types(db: Session = Depends(get_db)):
    ds = db.query(DocumentType).order_by(DocumentType.name).all()
    return [
        {
            "id": str(d.id),
            "code": d.code,
            "name": d.name,
            "country_id": str(d.country_id) if d.country_id else None,
            "format": d.format,
            "regex": d.regex,
            "is_active": d.is_active,
        }
        for d in ds
    ]


@router.post("/document-types", status_code=status.HTTP_201_CREATED)
def admin_create_document_type(
    data: DocumentTypeAdminCreate, db: Session = Depends(get_db)
):
    existing = (
        db.query(DocumentType).filter(DocumentType.code == data.code).first()
    )
    if existing:
        raise HTTPException(400, "Ya existe un tipo de documento con ese código")
    d = DocumentType(**data.model_dump())
    db.add(d)
    db.commit()
    db.refresh(d)
    return {
        "id": str(d.id),
        "code": d.code,
        "name": d.name,
        "country_id": str(d.country_id) if d.country_id else None,
        "format": d.format,
        "regex": d.regex,
        "is_active": d.is_active,
    }


@router.put("/document-types/{doc_type_id}")
def admin_update_document_type(
    doc_type_id: UUID,
    data: DocumentTypeAdminUpdate,
    db: Session = Depends(get_db),
):
    d = _get_or_404(db, DocumentType, doc_type_id, "Tipo de documento")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(d, key, value)
    db.commit()
    db.refresh(d)
    return {
        "id": str(d.id),
        "code": d.code,
        "name": d.name,
        "country_id": str(d.country_id) if d.country_id else None,
        "format": d.format,
        "regex": d.regex,
        "is_active": d.is_active,
    }