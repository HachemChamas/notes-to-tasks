"""Task extraction with Google Gemini.

Gemini must answer with JSON matching AIResult (response_schema), the same
shape the Claude version uses, so the rest of the app can't tell the
difference.

Free-tier Gemini models are sometimes overloaded or out of quota. When that
happens we try GEMINI_FALLBACK_MODEL once before giving up.
"""

import logging
from datetime import date

import httpx
from google import genai
from google.genai import errors, types

from app.config import GEMINI_API_KEY, GEMINI_FALLBACK_MODEL, GEMINI_MODEL
from app.extractor import SYSTEM_PROMPT, AIResult, ExtractionError, build_prompt, clean_tasks
from app.schemas import SuggestedTask

logger = logging.getLogger(__name__)

TIMEOUT_MS = 60_000  # give up on a request after 60 seconds

# Worth trying the fallback model: rate limit / quota, server errors,
# overloaded ("high demand") and timeouts.
_RETRYABLE_CODES = {429, 500, 502, 503, 504}

# Gemini's reasons for stopping without an answer because of its safety rules.
_BLOCKED_REASONS = {"SAFETY", "PROHIBITED_CONTENT", "BLOCKLIST", "SPII", "RECITATION"}


def make_gemini_client(api_key: str | None = GEMINI_API_KEY) -> genai.Client | None:
    """A Gemini client, or None when no key is set (extract() then explains)."""
    if not api_key:
        return None
    return genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=TIMEOUT_MS))


class GeminiExtractor:
    def __init__(
        self,
        client: genai.Client | None,
        model: str = GEMINI_MODEL,
        fallback_model: str | None = GEMINI_FALLBACK_MODEL,
    ):
        self.client = client
        # The models to try, in order (no duplicates).
        self.models = [model] + ([fallback_model] if fallback_model and fallback_model != model else [])

    def extract(self, text: str, meeting_date: date, team: list[str]) -> list[SuggestedTask]:
        if self.client is None:
            raise ExtractionError(
                "No Gemini API key is set. Add GEMINI_API_KEY to .env and restart the backend.",
                status_code=503,
            )

        prompt = build_prompt(text, meeting_date, team)
        for attempt, model in enumerate(self.models):
            is_last = attempt == len(self.models) - 1
            try:
                response = self.client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        response_mime_type="application/json",
                        response_schema=AIResult,
                    ),
                )
            except errors.APIError as error:
                if error.code in _RETRYABLE_CODES and not is_last:
                    logger.warning("Gemini %s failed (%s), trying %s", model, error.code, self.models[attempt + 1])
                    continue
                raise _explain_api_error(error, model) from error
            except httpx.TimeoutException:
                if not is_last:
                    logger.warning("Gemini %s timed out, trying %s", model, self.models[attempt + 1])
                    continue
                raise ExtractionError("Gemini took too long to answer. Try again.", status_code=503)
            except httpx.HTTPError:
                raise ExtractionError("Could not reach Gemini. Check your internet connection.", status_code=503)

            return clean_tasks(_parsed_result(response))

        raise AssertionError("unreachable: the loop always returns or raises")


def _parsed_result(response: types.GenerateContentResponse) -> AIResult:
    """The validated AIResult, or a clear error explaining why there isn't one."""
    if isinstance(response.parsed, AIResult):
        return response.parsed

    # No usable answer. Work out why, so the user gets a helpful message.
    feedback = response.prompt_feedback
    finish = response.candidates[0].finish_reason if response.candidates else None
    finish_name = getattr(finish, "name", str(finish))
    if (feedback and feedback.block_reason) or finish_name in _BLOCKED_REASONS:
        raise ExtractionError("Gemini declined to process these notes.", status_code=422)
    if finish_name == "MAX_TOKENS":
        raise ExtractionError("Gemini's answer was cut off. Try pasting shorter notes.", status_code=422)
    raise ExtractionError("Gemini sent an answer we couldn't read. Try again.", status_code=502)


def _explain_api_error(error: errors.APIError, model: str) -> ExtractionError:
    logger.warning("Gemini API error %s %s: %s", error.code, error.status, error.message)
    message = (error.message or "").lower()
    if error.code in (401, 403) or (error.code == 400 and "api key" in message):
        return ExtractionError(
            "Gemini rejected the API key. Check GEMINI_API_KEY in .env.", status_code=503
        )
    if error.code == 429:
        return ExtractionError(
            "Gemini's free-tier limit was reached. Wait a minute and try again.", status_code=503
        )
    if error.code == 404:
        return ExtractionError(
            f'The Gemini model "{model}" isn\'t available. Change GEMINI_MODEL in .env.',
            status_code=502,
        )
    if error.code >= 500:
        return ExtractionError(
            "Gemini is overloaded right now. Try again in a minute.", status_code=503
        )
    return ExtractionError("Gemini returned an error.", status_code=502)
