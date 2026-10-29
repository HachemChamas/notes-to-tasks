"""Tests for app/extractor.py, the part that talks to Claude."""

import json
from datetime import date

import anthropic
import httpx2
import pytest

from app.extractor import (
    AIResult,
    AITask,
    ExtractionError,
    TaskExtractor,
    build_prompt,
    clean_tasks,
)


def test_prompt_includes_date_weekday_team_and_notes():
    prompt = build_prompt("Ada: I'll do it", date(2026, 10, 29), ["Ada", "Alan"])

    assert "Meeting date: 2026-10-29 (Thursday)" in prompt
    assert "Team list: Ada, Alan" in prompt
    assert "<notes>\nAda: I'll do it\n</notes>" in prompt


def test_clean_tasks_fixes_messy_ai_output():
    result = AIResult(
        tasks=[
            AITask(title="  Send budget ", description=" ", owner_name=" Ada ", due_date="2026-11-06"),
            AITask(title="   ", description=None, owner_name=None, due_date=None),
            AITask(title="Call client", description=None, owner_name="", due_date="next Friday"),
        ]
    )

    tasks = clean_tasks(result)

    assert len(tasks) == 2  # the task with a blank title is dropped
    assert tasks[0].title == "Send budget"
    assert tasks[0].description is None
    assert tasks[0].owner_name == "Ada"
    assert tasks[0].due_date == date(2026, 11, 6)
    assert tasks[1].owner_name is None
    assert tasks[1].due_date is None  # not a real date, so it is dropped


# ---------------------------------------------------------------------------
# The tests below run the real TaskExtractor and the real anthropic SDK, but
# swap the network for a fake (MockTransport), so nothing leaves the machine.
# They check that we send a sensible request and handle every kind of answer.
# ---------------------------------------------------------------------------
def fake_claude(status_code=200, stop_reason="end_turn", answer=None, sent=None):
    """An anthropic client whose 'network' returns the response we choose."""

    def handler(request):
        if sent is not None:
            sent.append(json.loads(request.content))
        if status_code != 200:
            return httpx2.Response(status_code, json={"type": "error", "error": {"type": "x", "message": "x"}})
        return httpx2.Response(
            200,
            json={
                "id": "msg_test",
                "type": "message",
                "role": "assistant",
                "model": "claude-opus-5-5",
                "content": [{"type": "text", "text": json.dumps(answer or {"tasks": []})}],
                "stop_reason": stop_reason,
                "stop_sequence": None,
                "usage": {"input_tokens": 1, "output_tokens": 1},
            },
        )

    return anthropic.Anthropic(
        api_key="test-key",
        max_retries=0,
        http_client=httpx2.Client(transport=httpx2.MockTransport(handler)),
    )


def test_extract_sends_notes_and_parses_the_answer():
    sent = []
    answer = {"tasks": [{"title": "Send budget", "description": None, "owner_name": "Ada", "due_date": "2026-11-02"}]}
    extractor = TaskExtractor(fake_claude(answer=answer, sent=sent), model="claude-opus-5-5")

    tasks = extractor.extract("Ada sends the budget Monday", date(2026, 10, 29), ["Ada"])

    assert tasks[0].title == "Send budget"
    assert tasks[0].due_date == date(2026, 11, 2)
    request = sent[0]
    assert request["model"] == "claude-opus-5-5"
    assert "Ada sends the budget Monday" in request["messages"][0]["content"]
    assert request["output_config"]["format"]["type"] == "json_schema"
    assert request["fallbacks"] == "default"


def test_refusal_becomes_a_clear_error():
    extractor = TaskExtractor(fake_claude(stop_reason="refusal"))

    with pytest.raises(ExtractionError) as error:
        extractor.extract("notes", date(2026, 10, 29), [])

    assert error.value.status_code == 422


@pytest.mark.parametrize("status_code, expected", [(401, 503), (429, 503), (500, 502)])
def test_api_errors_become_clear_errors(status_code, expected):
    extractor = TaskExtractor(fake_claude(status_code=status_code))

    with pytest.raises(ExtractionError) as error:
        extractor.extract("notes", date(2026, 10, 29), [])

    assert error.value.status_code == expected


def test_missing_api_key_becomes_a_clear_error(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_AUTH_TOKEN", raising=False)
    client = anthropic.Anthropic(
        api_key=None, http_client=httpx2.Client(transport=httpx2.MockTransport(lambda r: None))
    )

    with pytest.raises(ExtractionError) as error:
        TaskExtractor(client).extract("notes", date(2026, 10, 29), [])

    assert "ANTHROPIC_API_KEY" in error.value.message
