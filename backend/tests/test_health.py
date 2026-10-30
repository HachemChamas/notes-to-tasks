"""Tests for the /health endpoint."""

from app.database import check_database
from app.main import app


def test_health_when_database_is_up(client):
    # Replace the real check_database() with a fake that always says
    # "the database is fine". FastAPI will call our fake instead.
    app.dependency_overrides[check_database] = lambda: True

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


def test_health_when_database_is_down(client):
    # The API itself still answers, but reports the database as unavailable.
    app.dependency_overrides[check_database] = lambda: False

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "unavailable"}
