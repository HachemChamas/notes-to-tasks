"""Shared setup for all backend tests. pytest loads this file automatically.

Our tests never touch a real database, so they run without Docker.
"""

import os

# app/config.py refuses to start without DATABASE_URL. Give it a fake one
# BEFORE the app is imported below. Nothing ever connects to it, because
# the tests replace the database functions with fakes.
os.environ.setdefault(
    "DATABASE_URL", "postgresql+psycopg://test:test@localhost:5432/test"
)

import pytest  # noqa: E402  (imports must come after setting the variable)
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture
def client():
    """A fake browser that sends requests straight to our app.

    Any test that has a `client` parameter gets one of these.
    After the test, we remove any fake dependencies it installed so the
    next test starts clean.
    """
    yield TestClient(app)
    app.dependency_overrides.clear()
