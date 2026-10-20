"""Configuración de tests.

Patrón:
- Una conexión con transacción global por test.
- Rollback al final → BD limpia entre tests.
- Los schemas de tenant se crean y se dropean por test.
"""

from collections.abc import Generator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models import (
    Attribute,
    AttributeType,
    Base,
    Category,
    Country,
    Currency,
    Permission,
    Plan,
    PlanFeature,
    PlanLimit,
    Profile,
    Resource,
    Role,
    RolePermission,
    StockLot,
    Subcategory,
    Supplier,
    Tax,
    Tenant,
    Timezone,
    Unit,
    UnitCategory,
    User,
    UserRole,
    Vertical,
    Warehouse,
)

# ---------------------------------------------------------------------------
# Engine de test
# ---------------------------------------------------------------------------

TEST_DATABASE_URL = settings.DATABASE_URL.replace("boe_dev", "boe_test")

engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


# ---------------------------------------------------------------------------
# BD: crear tablas globales al inicio de la sesión
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def _setup_database():
    """Crea las tablas globales (public) al inicio de la sesión."""
    with engine.connect() as conn:
        conn.execute(text("SET search_path TO public"))
        conn.commit()

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


# ---------------------------------------------------------------------------
# Sesión con transacción reversible por test
# ---------------------------------------------------------------------------

@pytest.fixture
def db() -> Generator[Session, None, None]:
    """Sesión de BD con transacción que se revierte al final del test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


# ---------------------------------------------------------------------------
# Cliente HTTP
# ---------------------------------------------------------------------------

@pytest.fixture
def client(db: Session) -> Generator[TestClient, None, None]:
    """Cliente de test con la sesión de BD del test."""

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Factories multi-tenant
# ---------------------------------------------------------------------------

@pytest.fixture
def tenant_factory(db: Session):
    """Crea tenants de prueba con schema real y tablas operativas completas."""
    from app.services.tenant_service import create_tenant_schema

    created_schemas: list[str] = []

    def _create(
        name: str = "Test Tenant",
        tax_id: str | None = None,
    ) -> Tenant:
        uid = uuid4().hex
        schema_name = f"tenant_test_{uid[:16]}"
        tenant = Tenant(
            name=name,
            tax_id=tax_id or f"TEST-{uid[:12]}",
            tax_id_type="TEST",
            admin_email=f"admin-{uid[:8]}@test.com",
            timezone="America/Caracas",
            country="Venezuela",
            schema_name=schema_name,
            status="activo",
        )
        db.add(tenant)
        db.flush()
        create_tenant_schema(db, schema_name)
        created_schemas.append(schema_name)
        return tenant

    yield _create

    for schema in created_schemas:
        db.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))
    db.flush()


@pytest.fixture
def user_factory(db: Session):
    """Crea users de prueba en un tenant con todos los permisos."""

    def _create(
        tenant: Tenant,
        email: str | None = None,
        password: str = "password123",
        status: str = "activo",
    ) -> tuple[User, str]:
        uid = uuid4().hex
        user = User(
            tenant_id=tenant.id,
            email=email or f"user-{uid[:8]}@test.com",
            password_hash=hash_password(password),
            first_name="Test",
            last_name="User",
            phone=None,
            phone_verified=True,
            status=status,
        )
        db.add(user)
        db.flush()

        role = Role(
            name=f"TestRole_{uid[:8]}",
            description="Test role with all permissions",
            is_system=False,
        )
        db.add(role)
        db.flush()

        all_perms = db.query(Permission).all()
        for perm in all_perms:
            db.add(RolePermission(role_id=role.id, permission_id=perm.id))
        db.flush()

        db.add(UserRole(user_id=user.id, role_id=role.id))
        db.flush()

        return user, password

    return _create


@pytest.fixture
def token_for_user():
    """Genera JWT para un user."""

    def _make(user: User) -> str:
        return create_access_token(subject=str(user.id))

    return _make


# ---------------------------------------------------------------------------
# Fixtures legacy
# ---------------------------------------------------------------------------

@pytest.fixture
def vertical(db: Session) -> Vertical:
    uid = uuid4().hex
    v = Vertical(
        code=f"test_vertical_{uid[:8]}",
        name=f"Test Vertical {uid[:8]}",
        description="Test",
    )
    db.add(v)
    db.flush()
    return v


@pytest.fixture
def plan(db: Session, currency) -> Plan:
    uid = uuid4().hex
    p = Plan(
        code=f"test_plan_{uid[:8]}",
        name=f"Test Plan {uid[:8]}",
        price=39.00,
        currency_id=currency.id,
        interval="monthly",
        trial_days=14,
        is_active=True,
    )
    db.add(p)
    db.flush()
    return p


@pytest.fixture
def profile(db: Session) -> Profile:
    uid = uuid4().hex
    p = Profile(name=f"Test Profile {uid[:8]}", description="Test")
    db.add(p)
    db.flush()
    return p


@pytest.fixture
def permission(db: Session) -> Permission:
    uid = uuid4().hex
    p = Permission(module=f"test-{uid[:6]}", action="ver", description="Test")
    db.add(p)
    db.flush()
    return p


@pytest.fixture
def tenant(db: Session, tenant_factory) -> Tenant:
    return tenant_factory(name="Test Tenant")


@pytest.fixture
def user(db: Session, tenant: Tenant, user_factory) -> User:
    user, _ = user_factory(
        tenant=tenant,
        email=f"test-{uuid4().hex[:8]}@test.com",
        password="password123",
    )
    return user


@pytest.fixture
def auth_headers(client: TestClient, user: User) -> dict:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": user.email, "password": "password123"},
    )
    assert response.status_code == 200, f"Login falló: {response.json()}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def currency(db: Session) -> Currency:
    uid = uuid4().hex
    c = Currency(
        code=f"TST{uid[:3].upper()}",
        name=f"Test Currency {uid[:6]}",
        symbol="T$",
        decimals=2,
        is_base=False,
    )
    db.add(c)
    db.flush()
    return c


# ---------------------------------------------------------------------------
# Fixtures de datos maestros
# ---------------------------------------------------------------------------

@pytest.fixture
def unit(db: Session) -> Unit:
    cat = db.query(UnitCategory).filter(UnitCategory.code == "test_peso").first()
    if not cat:
        cat = UnitCategory(code="test_peso", name="Test Peso")
        db.add(cat)
        db.flush()
    uid = uuid4().hex[:6]
    u = Unit(
        code=f"tkg_{uid}",
        name=f"Test Kilogramo {uid}",
        symbol="tkg",
        category_id=cat.id,
        is_base=True,
    )
    db.add(u)
    db.flush()
    return u


@pytest.fixture
def category(db: Session) -> Category:
    uid = uuid4().hex[:6]
    c = Category(code=f"test_cat_{uid}", name=f"Test Category {uid}")
    db.add(c)
    db.flush()
    return c


@pytest.fixture
def subcategory(db: Session, category) -> Subcategory:
    uid = uuid4().hex[:6]
    s = Subcategory(
        category_id=category.id,
        code=f"test_sub_{uid}",
        name=f"Test Subcategory {uid}",
    )
    db.add(s)
    db.flush()
    return s


@pytest.fixture
def attribute(db: Session) -> Attribute:
    at = db.query(AttributeType).filter(AttributeType.code == "boolean").first()
    if not at:
        at = AttributeType(code="boolean", name="Booleano")
        db.add(at)
        db.flush()
    uid = uuid4().hex[:6]
    a = Attribute(
        code=f"test_attr_{uid}",
        name=f"Test Attribute {uid}",
        type_id=at.id,
    )
    db.add(a)
    db.flush()
    return a


@pytest.fixture
def tax(db: Session, country) -> Tax:
    uid = uuid4().hex[:6]
    t = Tax(
        country_id=country.id,
        code=f"TEST_TAX_{uid}",
        name=f"Test Tax {uid}",
        rate=16.00,
        applies_to="general",
    )
    db.add(t)
    db.flush()
    return t


@pytest.fixture
def country(db: Session) -> Country:
    tz = db.query(Timezone).filter(Timezone.code == "America/Caracas").first()
    if not tz:
        tz = Timezone(
            code="America/Caracas",
            friendly_name="Venezuela",
            utc_offset="UTC-4",
        )
        db.add(tz)
        db.flush()
    cur = db.query(Currency).filter(Currency.code == "USD").first()
    if not cur:
        cur = Currency(
            code="USD",
            name="Dólar",
            symbol="$",
            decimals=2,
            is_base=True,
        )
        db.add(cur)
        db.flush()
    uid = uuid4().hex[:6]
    code = f"X{uid[0].upper()}"
    existing = db.query(Country).filter(Country.code == code).first()
    if existing:
        code = f"Y{uid[1].upper()}"
    c = Country(
        code=code,
        name=f"Test Country {uid}",
        timezone_id=tz.id,
        currency_id=cur.id,
        phone_prefix="+999",
    )
    db.add(c)
    db.flush()
    return c


@pytest.fixture
def cleanup_register_schemas(db: Session):
    schemas_to_drop: list[str] = []
    yield schemas_to_drop
    for schema in schemas_to_drop:
        try:
            db.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))
        except Exception:
            pass
    db.commit()


# ---------------------------------------------------------------------------
# Fixtures para tests de availability
# ---------------------------------------------------------------------------

@pytest.fixture
def resource(db: Session, tenant, unit) -> Resource:
    """Crea un recurso en el schema del tenant."""
    db.execute(
        text(f'SET LOCAL search_path TO "{tenant.schema_name}", public')
    )
    uid = uuid4().hex[:6]
    r = Resource(
        name=f"Recurso {uid}",
        resource_type="materia_prima",
        base_unit_id=unit.id,
        cost=10.0,
        waste_percent=0,
        is_active=True,
    )
    db.add(r)
    db.flush()
    return r


@pytest.fixture
def stock_lot(db: Session, tenant, resource) -> StockLot:
    """Crea un lote de stock de prueba (5 unidades)."""
    from datetime import datetime, timezone
    from decimal import Decimal

    db.execute(
        text(f'SET LOCAL search_path TO "{tenant.schema_name}", public')
    )
    wh = db.query(Warehouse).filter(Warehouse.code == "TEST-WH").first()
    if not wh:
        wh = Warehouse(name="Test Warehouse", code="TEST-WH", is_active=True)
        db.add(wh)
        db.flush()
    lot = StockLot(
        warehouse_id=wh.id,
        resource_id=resource.id,
        lot_code=f"LOT-{uuid4().hex[:6]}",
        quantity=Decimal("5"),
        received_at=datetime.now(timezone.utc),
    )
    db.add(lot)
    db.flush()
    return lot


@pytest.fixture
def supplier_with_offer(db: Session, tenant, resource) -> Supplier:
    """Crea un proveedor con oferta para el recurso."""
    from decimal import Decimal
    from app.models import SupplierResource

    db.execute(
        text(f'SET LOCAL search_path TO "{tenant.schema_name}", public')
    )
    uid = uuid4().hex[:6]
    s = Supplier(code=f"SUP-{uid}", name=f"Proveedor {uid}", is_active=True)
    db.add(s)
    db.flush()
    sr = SupplierResource(
        supplier_id=s.id,
        resource_id=resource.id,
        unit_price=Decimal("2.50"),
        lead_time_days=3,
        min_quantity=Decimal("1"),
    )
    db.add(sr)
    db.flush()
    return s


@pytest.fixture
def stock_lot_from_other_tenant(db: Session, tenant_factory) -> StockLot:
    """Crea un stock_lot en un tenant distinto (para probar aislamiento)."""
    from datetime import datetime, timezone
    from decimal import Decimal

    other_tenant = tenant_factory(name="Other Tenant for Availability")
    db.execute(
        text(f'SET LOCAL search_path TO "{other_tenant.schema_name}", public')
    )
    cat = db.query(UnitCategory).filter(UnitCategory.code == "test_peso").first()
    if not cat:
        cat = UnitCategory(code="test_peso", name="Test Peso")
        db.add(cat)
        db.flush()
    u = Unit(
        code=f"other_kg_{uuid4().hex[:4]}",
        name="Other Kilogramo",
        symbol="okg",
        category_id=cat.id,
        is_base=True,
    )
    db.add(u)
    db.flush()
    r = Resource(
        name=f"Recurso Other {uuid4().hex[:6]}",
        resource_type="materia_prima",
        base_unit_id=u.id,
        cost=10.0,
        waste_percent=0,
        is_active=True,
    )
    db.add(r)
    db.flush()
    wh = Warehouse(
        name="Other Warehouse",
        code=f"OWH-{uuid4().hex[:6]}",
        is_active=True,
    )
    db.add(wh)
    db.flush()
    lot = StockLot(
        warehouse_id=wh.id,
        resource_id=r.id,
        lot_code=f"LOT-O-{uuid4().hex[:6]}",
        quantity=Decimal("100"),
        received_at=datetime.now(timezone.utc),
    )
    db.add(lot)
    db.flush()
    return lot


# ---------------------------------------------------------------------------
# Seeds mínimos para boe_test
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def _seed_minimal_data(_setup_database):
    """Carga datos maestros mínimos en boe_test (una vez por sesión)."""
    from decimal import Decimal
    from app.models import Feature

    session = TestingSessionLocal()
    try:
        # Timezone Venezuela
        tz = session.query(Timezone).filter(Timezone.code == "America/Caracas").first()
        if not tz:
            tz = Timezone(code="America/Caracas", friendly_name="Venezuela", utc_offset="UTC-4")
            session.add(tz)
            session.flush()

        # Currency USD
        usd = session.query(Currency).filter(Currency.code == "USD").first()
        if not usd:
            usd = Currency(code="USD", name="Dólar estadounidense", symbol="$", decimals=2, is_base=True)
            session.add(usd)
            session.flush()

        # Country VE
        ve = session.query(Country).filter(Country.code == "VE").first()
        if not ve:
            ve = Country(code="VE", name="Venezuela", timezone_id=tz.id, currency_id=usd.id, phone_prefix="+58")
            session.add(ve)
            session.flush()

        # Vertical
        v = session.query(Vertical).filter(Vertical.code == "clinicas_generales").first()
        if not v:
            v = Vertical(code="clinicas_generales", name="Clínicas generales", description="Clínicas médicas generales")
            session.add(v)
            session.flush()

        # Permisos (INCLUYENDO inventory:ver_costos)
        permissions_data = [
            ("resource", "crear"), ("resource", "ver"), ("resource", "editar"), ("resource", "eliminar"),
            ("supplier", "crear"), ("supplier", "ver"), ("supplier", "editar"), ("supplier", "eliminar"),
            ("bundle", "crear"), ("bundle", "ver"), ("bundle", "editar"), ("bundle", "eliminar"),
            ("purchase_request", "crear"), ("purchase_request", "ver"), ("purchase_request", "editar"), ("purchase_request", "eliminar"), ("purchase_request", "aprobar"),
            ("supplier_quote", "ver"), ("supplier_quote", "crear"), ("supplier_quote", "editar"), ("supplier_quote", "eliminar"), ("supplier_quote", "seleccionar"),
            ("warehouse", "crear"), ("warehouse", "ver"), ("warehouse", "editar"), ("warehouse", "eliminar"),
            ("movement", "crear"), ("movement", "ver"),
            ("inventory", "ver"), ("inventory", "ver_costos"), ("inventory", "ver_lotes"), ("inventory", "crear"), ("inventory", "editar"), ("inventory", "eliminar"),
            ("production", "ver"), ("production", "crear"), ("production", "editar"), ("production", "eliminar"),
            ("tenant", "configurar"), ("tenant", "ver_usuarios"), ("tenant", "gestionar_roles"), ("tenant", "gestionar_permisos"),
        ]
        for module, action in permissions_data:
            existing = session.query(Permission).filter(Permission.module == module, Permission.action == action).first()
            if not existing:
                session.add(Permission(module=module, action=action, description=f"{action} {module}"))
        session.flush()

        # Roles
        for role_name in ["Admin", "Editor", "Lector", "SuperAdmin"]:
            existing = session.query(Role).filter(Role.name == role_name).first()
            if not existing:
                session.add(Role(name=role_name, description=role_name, is_system=True))
        session.flush()

        # Features
        feature_codes = ["inventario", "planificacion", "marketplace", "notificaciones"]
        features: dict[str, Feature] = {}
        for code in feature_codes:
            f = session.query(Feature).filter(Feature.code == code).first()
            if not f:
                f = Feature(code=code, name=code.title(), description=f"Feature {code}", applies_to="both")
                session.add(f)
                session.flush()
            features[code] = f

        # Planes
        plans_data = [
            {"code": "mpr_base", "name": "MPR Base", "price": Decimal("39.00"), "interval": "monthly", "trial_days": 14, "features": ["inventario", "planificacion", "notificaciones"], "limits": {"recursos": 50, "usuarios": 3, "paquetes": 10}},
            {"code": "mpr_plus", "name": "MPR Plus", "price": Decimal("79.00"), "interval": "monthly", "trial_days": 14, "features": ["inventario", "planificacion", "marketplace", "notificaciones"], "limits": {"recursos": None, "usuarios": 10, "paquetes": None}},
            {"code": "mp_gratuito", "name": "Marketplace Gratuito", "price": Decimal("0.00"), "interval": "monthly", "trial_days": 0, "features": ["marketplace", "notificaciones"], "limits": {"productos": 10, "ventas_mes": 3, "leads_mes": 3}},
            {"code": "mp_basico", "name": "Marketplace Basico", "price": Decimal("19.00"), "interval": "monthly", "trial_days": 0, "features": ["marketplace", "notificaciones"], "limits": {"productos": 100, "ventas_mes": 20, "leads_mes": 10}},
            {"code": "mp_plus", "name": "Marketplace Plus", "price": Decimal("35.00"), "interval": "monthly", "trial_days": 0, "features": ["marketplace", "notificaciones"], "limits": {"productos": None, "ventas_mes": 40, "leads_mes": 30}},
        ]
        for pdata in plans_data:
            existing = session.query(Plan).filter(Plan.code == pdata["code"]).first()
            if existing:
                continue
            plan = Plan(code=pdata["code"], name=pdata["name"], price=pdata["price"], currency_id=usd.id, interval=pdata["interval"], trial_days=pdata["trial_days"], is_active=True)
            session.add(plan)
            session.flush()
            for fcode in pdata["features"]:
                feature = features.get(fcode)
                if feature:
                    session.add(PlanFeature(plan_id=plan.id, feature_id=feature.id))
            for lcode, lvalue in pdata["limits"].items():
                session.add(PlanLimit(plan_id=plan.id, limit_code=lcode, value=lvalue))

        session.commit()
    finally:
        session.close()