"""Tests for the /health endpoint."""

import pytest

from app.database import check_database
from app.main import app


def test_health_when_database_is_up(client):
    # Replace the real check_database() with a fake that always says
    # "the database is fine". FastAPI will call our fake instead.
    app.dependency_overrides[check_database] = lambda: True

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


@pytest.mark.skip(reason="TODO (test): write this test, then delete this line")
def test_health_when_database_is_down(client):
    # ----------------------------------------------------------------------
    # TODO (test): write this test.
    #
    # What it should check:
    #   When the database can NOT be reached, /health still answers with
    #   status code 200, but the JSON says the database is unavailable:
    #       {"status": "ok", "database": "unavailable"}
    #
    # How:
    #   1. Use the test above as your example.
    #   2. Make the fake check_database return False instead of True.
    #   3. Call /health and assert on the status code and the JSON.
    #   4. Delete the @pytest.mark.skip line above this function.
    #
    # How to check it works:
    #   Run `pytest`. It should say "2 passed" instead of
    #   "1 passed, 1 skipped". Then break it on purpose (expect "ok")
    #   and check that it fails, so you know the test really tests something.
    # ----------------------------------------------------------------------
    ...
