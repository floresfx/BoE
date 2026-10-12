from fastapi.testclient import TestClient

from app.models import User


def test_create_device(client: TestClient, auth_headers: dict):
    """Test: crear un dispositivo seguro."""
    response = client.post(
        "/api/v1/secure-devices",
        headers=auth_headers,
        json={
            "fingerprint": "device-fingerprint-1",
            "ip": "192.168.1.1",
        },
    )
    assert response.status_code == 201


def test_create_device_maximo(client: TestClient, auth_headers: dict):
    """Test: no permitir más de 2 dispositivos."""
    # Crear 2
    for i in range(2):
        client.post(
            "/api/v1/secure-devices",
            headers=auth_headers,
            json={"fingerprint": f"fp-{i}", "ip": "192.168.1.1"},
        )

    # Intentar crear el tercero
    response = client.post(
        "/api/v1/secure-devices",
        headers=auth_headers,
        json={"fingerprint": "fp-3", "ip": "192.168.1.1"},
    )
    assert response.status_code == 400


def test_list_devices(client: TestClient, auth_headers: dict):
    """Test: listar dispositivos."""
    response = client.get("/api/v1/secure-devices", headers=auth_headers)
    assert response.status_code == 200


def test_delete_device(client: TestClient, auth_headers: dict):
    """Test: eliminar un dispositivo."""
    # Crear
    create_response = client.post(
        "/api/v1/secure-devices",
        headers=auth_headers,
        json={"fingerprint": "fp-delete", "ip": "192.168.1.1"},
    )
    device_id = create_response.json()["id"]

    # Eliminar
    response = client.delete(
        f"/api/v1/secure-devices/{device_id}",
        headers=auth_headers,
    )
    assert response.status_code == 204