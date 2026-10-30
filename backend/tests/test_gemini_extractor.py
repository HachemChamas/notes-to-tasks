"""Tests for the Gemini provider.

They use the real google-genai SDK, but swap the network for a fake
(httpx.MockTransport) that answers like Gemini would. Nothing leaves the
machine and no API key is needed.
"""

import json
from datetime import date

import httpx
import pytest
from google import genai
from google.genai import types

from app.extractor import ExtractionError
from app.gemini_extractor import GeminiExtractor, make_gemini_client


def answer(tasks=None, finish="STOP"):
    """A successful Gemini response whose text is our JSON."""
    return httpx.Response(
        200,
        json={
            "candidates": [
                {
                    "content": {"role": "model", "parts": [{"text": json.dumps({"tasks": tasks or []})}]},
                    "finishReason": finish,
                }
            ]
        },
    )


def task(title):
    """A task with every field filled in, as the schema requires."""
    return {"title": title, "description": None, "owner_name": None, "due_date": None}


def api_error(code, status, message="error"):
    return httpx.Response(code, json={"error": {"code": code, "status": status, "message": message}})


def fake_gemini(*responses, sent=None):
    """A Gemini client whose 'server' replies with `responses`, in order."""
    replies = list(responses)

    def handler(request):
        if sent is not None:
            sent.append({"path": request.url.path, "body": json.loads(request.content)})
        reply = replies.pop(0)
        if isinstance(reply, Exception):
            raise reply
        return reply

    http = httpx.Client(transport=httpx.MockTransport(handler))
    return genai.Client(api_key="test-key", http_options=types.HttpOptions(httpx_client=http))


def extract(client, **kwargs):
    extractor = GeminiExtractor(client, model="main-model", fallback_model="backup-model", **kwargs)
    return extractor.extract("Ada sends the budget Monday", date(2026, 10, 29), ["Ada"])


def test_sends_prompt_and_schema_and_parses_the_answer():
    sent = []
    tasks = [{"title": "Send budget", "description": None, "owner_name": "Ada", "due_date": "2026-11-02"}]

    result = extract(fake_gemini(answer(tasks), sent=sent))

    assert result[0].title == "Send budget"
    assert result[0].due_date == date(2026, 11, 2)
    request = sent[0]
    assert request["path"].endswith("/models/main-model:generateContent")
    assert "Ada sends the budget Monday" in request["body"]["contents"][0]["parts"][0]["text"]
    assert "shared task board" in request["body"]["systemInstruction"]["parts"][0]["text"]
    assert request["body"]["generationConfig"]["responseMimeType"] == "application/json"
    assert "tasks" in json.dumps(request["body"]["generationConfig"]["responseSchema"])


@pytest.mark.parametrize("code, status", [(503, "UNAVAILABLE"), (429, "RESOURCE_EXHAUSTED"), (504, "DEADLINE_EXCEEDED")])
def test_falls_back_to_the_backup_model_when_overloaded(code, status):
    sent = []
    client = fake_gemini(api_error(code, status), answer([task("Send budget")]), sent=sent)

    result = extract(client)

    assert result[0].title == "Send budget"
    assert [s["path"].rsplit("/", 1)[-1] for s in sent] == [
        "main-model:generateContent",
        "backup-model:generateContent",
    ]


def test_falls_back_after_a_timeout():
    client = fake_gemini(httpx.ReadTimeout("slow"), answer([task("Send budget")]))

    assert extract(client)[0].title == "Send budget"


@pytest.mark.parametrize(
    "reply, status_code, words",
    [
        (api_error(400, "INVALID_ARGUMENT", "API key not valid. Please pass a valid API key."), 503, "API key"),
        (api_error(403, "PERMISSION_DENIED"), 503, "API key"),
        (api_error(404, "NOT_FOUND", "model is no longer available"), 502, "GEMINI_MODEL"),
        (api_error(400, "INVALID_ARGUMENT", "something else"), 502, "returned an error"),
    ],
)
def test_errors_that_a_fallback_cannot_fix_are_explained(reply, status_code, words):
    sent = []

    with pytest.raises(ExtractionError) as error:
        extract(fake_gemini(reply, sent=sent))

    assert error.value.status_code == status_code
    assert words in error.value.message
    assert len(sent) == 1  # no point trying the backup model


def test_when_both_models_are_busy_the_user_is_told_to_wait():
    client = fake_gemini(api_error(429, "RESOURCE_EXHAUSTED"), api_error(429, "RESOURCE_EXHAUSTED"))

    with pytest.raises(ExtractionError) as error:
        extract(client)

    assert error.value.status_code == 503
    assert "free-tier limit" in error.value.message


def test_blocked_answers_become_a_clear_error():
    blocked = httpx.Response(200, json={"promptFeedback": {"blockReason": "SAFETY"}})

    with pytest.raises(ExtractionError) as error:
        extract(fake_gemini(blocked))

    assert error.value.status_code == 422
    assert "declined" in error.value.message


def test_cut_off_answers_become_a_clear_error():
    cut_off = httpx.Response(
        200,
        json={"candidates": [{"content": {"role": "model", "parts": [{"text": '{"tasks": [{"ti'}]}, "finishReason": "MAX_TOKENS"}]},
    )

    with pytest.raises(ExtractionError) as error:
        extract(fake_gemini(cut_off))

    assert "cut off" in error.value.message


def test_missing_api_key_is_explained():
    assert make_gemini_client(api_key=None) is None

    with pytest.raises(ExtractionError) as error:
        GeminiExtractor(None).extract("notes", date(2026, 10, 29), [])

    assert "GEMINI_API_KEY" in error.value.message
