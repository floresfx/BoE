"""Tests de aislamiento multi-tenant.

Verifica que:
1. Un user de tenant A no ve users de tenant B.
2. Un user de tenant A no puede acceder a un user de tenant B por ID.
3. Los roles y permisos son globales (visibles desde ambos tenants).
4. El login no permite autenticar a un user con el token de otro.
"""

from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User


def test_users_aislados_por_tenant(
    client: TestClient,
    tenant_factory,
    user_factory,
    token_for_user,
):
    """User A no ve los users de tenant B."""
    # Dos tenants
    tenant_a = tenant_factory(name="Clínica A")
    tenant_b = tenant_factory(name="Panadería B")

    # Un user por tenant
    user_a, _ = user_factory(tenant_a, email=f"a-{uuid4().hex[:6]}@test.com")
    user_b, _ = user_factory(tenant_b, email=f"b-{uuid4().hex[:6]}@test.com")

    token_a = token_for_user(user_a)
    token_b = token_for_user(user_b)

    # A lista sus users
    r = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert r.status_code == 200
    items = r.json()["items"]
    emails = [u["email"] for u in items]

    assert user_a.email in emails
    assert user_b.email not in emails, "Fuga: A ve a un user de B"
    assert r.json()["total"] == 1

    # B lista sus users
    r = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert r.status_code == 200
    items = r.json()["items"]
    emails = [u["email"] for u in items]

    assert user_b.email in emails
    assert user_a.email not in emails, "Fuga: B ve a un user de A"
    assert r.json()["total"] == 1


def test_get_user_de_otro_tenant_devuelve_404(
    client: TestClient,
    tenant_factory,
    user_factory,
    token_for_user,
):
    """A no puede acceder a un user de B por ID directo."""
    tenant_a = tenant_factory(name="Clínica A")
    tenant_b = tenant_factory(name="Panadería B")

    user_a, _ = user_factory(tenant_a)
    user_b, _ = user_factory(tenant_b)

    token_a = token_for_user(user_a)

    r = client.get(
        f"/api/v1/users/{user_b.id}",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    # 404 porque get_user filtra por tenant del token
    assert r.status_code == 404


def test_roles_son_globales(
    client: TestClient,
    tenant_factory,
    user_factory,
    token_for_user,
    db: Session,
):
    """Roles son globales: se ven iguales desde cualquier tenant."""
    from app.models import Role
    # Crear rol único por test para no depender de seeds
    uid = uuid4().hex[:6]
    role = Role(name=f"TestRole-{uid}", description="Test", is_system=False)
    db.add(role)
    db.flush()

    tenant_a = tenant_factory(name="Clínica A")
    tenant_b = tenant_factory(name="Panadería B")
    user_a, _ = user_factory(tenant_a)
    user_b, _ = user_factory(tenant_b)

    token_a = token_for_user(user_a)
    token_b = token_for_user(user_b)

    r_a = client.get(
        "/api/v1/roles", headers={"Authorization": f"Bearer {token_a}"}
    )
    r_b = client.get(
        "/api/v1/roles", headers={"Authorization": f"Bearer {token_b}"}
    )

    assert r_a.status_code == 200
    assert r_b.status_code == 200

    names_a = sorted(x["name"] for x in r_a.json())
    names_b = sorted(x["name"] for x in r_b.json())

    assert names_a == names_b
    assert role.name in names_a


def test_login_aislado_por_email(
    client: TestClient,
    tenant_factory,
    user_factory,
):
    """Login usa email único global → no hay ambigüedad entre tenants."""
    tenant_a = tenant_factory(name="Clínica A")
    tenant_b = tenant_factory(name="Panadería B")

    email_a = f"shared-{uuid4().hex[:6]}@test.com"
    email_b = f"other-{uuid4().hex[:6]}@test.com"

    user_factory(tenant_a, email=email_a, password="pw_a_12345")
    user_factory(tenant_b, email=email_b, password="pw_b_12345")

    # Login correcto de A
    r = client.post(
        "/api/v1/auth/login",
        json={"email": email_a, "password": "pw_a_12345"},
    )
    assert r.status_code == 200
    assert r.json()["user"]["email"] == email_a

    # Login con password de B contra A → falla
    r = client.post(
        "/api/v1/auth/login",
        json={"email": email_a, "password": "pw_b_12345"},
    )
    assert r.status_code == 401


def test_search_path_no_contamina_entre_requests(
    client: TestClient,
    tenant_factory,
    user_factory,
    token_for_user,
):
    """Requests consecutivos de tenants distintos no comparten search_path."""
    tenant_a = tenant_factory(name="Clínica A")
    tenant_b = tenant_factory(name="Panadería B")

    user_a, _ = user_factory(tenant_a)
    user_b, _ = user_factory(tenant_b)

    token_a = token_for_user(user_a)
    token_b = token_for_user(user_b)

    # Request de A
    r1 = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert r1.status_code == 200
    emails_1 = [u["email"] for u in r1.json()["items"]]

    # Request de B inmediatamente después
    r2 = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert r2.status_code == 200
    emails_2 = [u["email"] for u in r2.json()["items"]]

    # Ninguno ve al otro
    assert user_a.email in emails_1
    assert user_b.email not in emails_1
    assert user_b.email in emails_2
    assert user_a.email not in emails_2