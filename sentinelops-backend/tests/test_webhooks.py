from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_webhook_access():
    # Spec 02 implementation returns 200 even without signature for now
    response = client.post("/api/webhooks/github", json={"action": "opened"})
    assert response.status_code == 200


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
