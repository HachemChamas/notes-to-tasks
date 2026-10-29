"""Shared setup for all backend tests. pytest loads this file automatically.

The tests never touch Postgres or the real AI:
- the database is a fresh in-memory SQLite database for every test
- the AI extractor is a fake that returns tasks we choose
So the whole suite runs in about a second, with no Docker and no API key.
"""

import os

# app/config.py refuses to start without DATABASE_URL. Give it a fake one
# BEFORE the app is imported below. Nothing ever connects to it.
os.environ.setdefault(
    "DATABASE_URL", "postgresql+psycopg://test:test@localhost:5432/test"
)

import pytest  # noqa: E402  (imports must come after setting the variable)
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.database import get_db  # noqa: E402
from app.extractor import get_extractor  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Base  # noqa: E402


class FakeExtractor:
    """Stands in for the real TaskExtractor. Records what it was asked."""

    def __init__(self):
        self.tasks = []  # what extract() will return; tests set this
        self.error = None  # set to an ExtractionError to simulate a failure
        self.calls = []

    def extract(self, text, meeting_date, team):
        self.calls.append({"text": text, "meeting_date": meeting_date, "team": team})
        if self.error:
            raise self.error
        return self.tasks


@pytest.fixture
def db_session():
    """A brand-new, empty in-memory database for one test."""
    # StaticPool reuses one connection, so every session sees the same
    # in-memory database (otherwise each connection would get its own).
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    yield session
    session.close()
    engine.dispose()


@pytest.fixture
def fake_extractor():
    return FakeExtractor()


@pytest.fixture
def client(db_session, fake_extractor):
    """A fake browser that sends requests straight to our app.

    dependency_overrides swaps the real database and AI for the test ones.
    After the test we remove the overrides so the next test starts clean.
    """
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_extractor] = lambda: fake_extractor
    yield TestClient(app)
    app.dependency_overrides.clear()
