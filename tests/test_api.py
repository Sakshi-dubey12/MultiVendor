import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_create_job_sync():
    response = client.post("/jobs", json={"vendor": "sync", "data": "test"})
    assert response.status_code == 200
    assert "request_id" in response.json()

def test_create_job_async():
    response = client.post("/jobs", json={"vendor": "async", "data": "test"})
    assert response.status_code == 200
    assert "request_id" in response.json()

def test_get_job_not_found():
    response = client.get("/jobs/doesnotexist")
    assert response.status_code == 404

def test_webhook():
    response = client.post("/vendor-webhook/async", json={"request_id": "testid", "result": "async vendor data"})
    assert response.status_code == 200
    assert response.json()["status"] == "ok" 