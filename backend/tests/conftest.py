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
    Base,
    Permission,
    Plan,
    Profile,
    Role,
    Tenant,
    User,
    Vertical,
)

# ---------------------------------------------------------------------------
# Engine de test (una sola vez por sesión)
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
    """Crea las tablas globales (public) al inicio de la sesión.

    NO las dropea al final: preferimos que boe_test quede con el esquema
    estándar entre ejecuciones. Si quieres limpiar, hazlo manualmente.
    """
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
# Cliente HTTP con override de get_db
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
    """Crea tenants de prueba con schema real.

    Devuelve una función `create(name=...)` que:
    - Genera tax_id y schema_name únicos.
    - Crea el schema en Postgres.
    - Registra el tenant en public.tenants.

    Al final del test, dropea todos los schemas creados.
    """
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
            base_currency="USD",
            timezone="America/Caracas",
            country="Venezuela",
            schema_name=schema_name,
            status="activo",
        )
        db.add(tenant)
        db.flush()
        db.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'))
        created_schemas.append(schema_name)
        return tenant

    yield _create

    for schema in created_schemas:
        db.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))
    db.flush()


@pytest.fixture
def user_factory(db: Session):
    """Crea users de prueba en un tenant."""

    def _create(
        tenant: Tenant,
        email: str | None = None,
        password: str = "password123",
        status: str = "activo",
    ) -> tuple[User, str]:
        """Devuelve (user, password_plaintext)."""
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
        return user, password

    return _create


@pytest.fixture
def token_for_user():
    """Genera JWT para un user."""

    def _make(user: User) -> str:
        return create_access_token(subject=str(user.id))

    return _make


# ---------------------------------------------------------------------------
# Fixtures legacy (compatibilidad con tests existentes)
# ---------------------------------------------------------------------------

@pytest.fixture
def vertical(db: Session) -> Vertical:
    """Crea un vertical de prueba."""
    uid = uuid4().hex
    v = Vertical(name=f"Test Vertical {uid[:8]}", description="Test")
    db.add(v)
    db.flush()
    return v


@pytest.fixture
def plan(db: Session) -> Plan:
    """Crea un plan de prueba."""
    uid = uuid4().hex
    p = Plan(
        name=f"Test Plan {uid[:8]}",
        description="Test",
        price=39.00,
        currency="USD",
        is_active=True,
    )
    db.add(p)
    db.flush()
    return p


@pytest.fixture
def profile(db: Session) -> Profile:
    """Crea un perfil de prueba."""
    uid = uuid4().hex
    p = Profile(name=f"Test Profile {uid[:8]}", description="Test")
    db.add(p)
    db.flush()
    return p


@pytest.fixture
def permission(db: Session) -> Permission:
    """Crea un permiso de prueba."""
    uid = uuid4().hex
    p = Permission(module=f"test-{uid[:6]}", action="ver", description="Test")
    db.add(p)
    db.flush()
    return p


@pytest.fixture
def tenant(db: Session, tenant_factory) -> Tenant:
    """Tenant de prueba simple (compatibilidad)."""
    return tenant_factory(name="Test Tenant")


@pytest.fixture
def user(db: Session, tenant: Tenant, user_factory) -> User:
    """Usuario de prueba simple (compatibilidad)."""
    user, _ = user_factory(
        tenant=tenant,
        email=f"test-{uuid4().hex[:8]}@test.com",
        password="password123",
    )
    return user


@pytest.fixture
def auth_headers(client: TestClient, user: User) -> dict:
    """Headers con JWT del usuario de prueba."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": user.email, "password": "password123"},
    )
    assert response.status_code == 200, f"Login falló: {response.json()}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}