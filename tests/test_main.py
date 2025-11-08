import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_read_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["message"] == "Welcome to Hackathon API"


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_docs_available():
    """Test that API documentation is available"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_api_v1_users_endpoint():
    """Test users endpoint exists"""
    response = client.get("/api/v1/users")
    # Should return 200 or appropriate status
    assert response.status_code in [200, 401, 403]
