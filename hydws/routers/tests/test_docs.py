from fastapi.testclient import TestClient
from hydws.main import app

client = TestClient(app)


def test_documentation():
    response = client.get("/docs")
    assert response.status_code == 200
