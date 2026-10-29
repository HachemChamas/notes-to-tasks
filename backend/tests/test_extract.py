"""Tests for POST /extract (the AI is faked, see conftest.py)."""

from datetime import date

from app.extractor import ExtractionError
from app.schemas import SuggestedTask


def test_extract_returns_suggestions_and_saves_the_note(client, fake_extractor):
    fake_extractor.tasks = [
        SuggestedTask(title="Send the budget", owner_name="Ada", due_date=date(2026, 11, 6))
    ]

    response = client.post(
        "/extract", json={"text": "Ada will send the budget by Friday", "meeting_date": "2026-11-02"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["note_id"] == 1
    assert body["tasks"] == [
        {"title": "Send the budget", "description": None, "owner_name": "Ada", "due_date": "2026-11-06"}
    ]
    # The meeting date we sent was passed through to the AI.
    assert fake_extractor.calls[0]["meeting_date"] == date(2026, 11, 2)


def test_extract_tells_the_ai_who_is_on_the_team(client, fake_extractor):
    client.post("/users", json={"name": "Grace"})
    client.post("/users", json={"name": "Ada"})

    client.post("/extract", json={"text": "some notes"})

    assert fake_extractor.calls[0]["team"] == ["Ada", "Grace"]  # sorted by name


def test_extract_reports_ai_errors(client, fake_extractor):
    fake_extractor.error = ExtractionError("The AI service is busy.", status_code=503)

    response = client.post("/extract", json={"text": "some notes"})

    assert response.status_code == 503
    assert response.json() == {"detail": "The AI service is busy."}


def test_extract_rejects_empty_text(client):
    response = client.post("/extract", json={"text": ""})

    assert response.status_code == 422
