from fastapi.testclient import TestClient

from app.models import User


def test_list_access_logs(client: TestClient, auth_headers: dict):
    """Test: listar logs de acceso."""
    response = client.get("/api/v1/access-logs", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)