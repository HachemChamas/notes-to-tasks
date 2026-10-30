"""Task extraction with Claude (Anthropic's API).

Claude must answer with JSON matching AIResult (structured outputs), and
API errors, refusals and missing keys become clear ExtractionErrors.
"""

import logging
from datetime import date

import anthropic

from app.config import ANTHROPIC_MODEL
from app.extractor import SYSTEM_PROMPT, AIResult, ExtractionError, build_prompt, clean_tasks
from app.schemas import SuggestedTask

logger = logging.getLogger(__name__)


class ClaudeExtractor:
    def __init__(self, client: anthropic.Anthropic, model: str = ANTHROPIC_MODEL):
        self.client = client
        self.model = model

    def extract(
        self, text: str, meeting_date: date, team: list[str]
    ) -> list[SuggestedTask]:
        try:
            response = self.client.beta.messages.parse(
                model=self.model,
                max_tokens=16000,
                system=SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": build_prompt(text, meeting_date, team)}
                ],
                # Claude must reply with JSON matching AIResult.
                output_format=AIResult,
                # "medium" thinking effort is plenty for pulling out tasks.
                output_config={"effort": "medium"},
                # If the model declines a request, the API retries it on a
                # suitable fallback model instead of failing.
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
            )
        except TypeError as error:
            # The SDK raises TypeError before sending anything when it finds
            # no credentials at all (e.g. ANTHROPIC_API_KEY is blank).
            logger.warning("Claude client not configured: %s", error)
            raise ExtractionError(
                "No Claude API key is set. Add ANTHROPIC_API_KEY to .env and restart the backend.",
                status_code=503,
            )
        except anthropic.AuthenticationError:
            raise ExtractionError(
                "The AI service rejected our credentials. Check ANTHROPIC_API_KEY in .env.",
                status_code=503,
            )
        except anthropic.RateLimitError:
            raise ExtractionError(
                "The AI service is busy (rate limited). Try again in a minute.",
                status_code=503,
            )
        except anthropic.APIConnectionError:
            raise ExtractionError("Could not reach the AI service.", status_code=503)
        except anthropic.APIStatusError as error:
            logger.warning("Claude API error %s: %s", error.status_code, error.message)
            raise ExtractionError("The AI service returned an error.", status_code=502)

        # Always check why the model stopped before reading the answer.
        if response.stop_reason == "refusal":
            raise ExtractionError(
                "The AI declined to process these notes.", status_code=422
            )
        if response.stop_reason == "max_tokens" or response.parsed_output is None:
            raise ExtractionError(
                "The AI's answer was cut off. Try pasting shorter notes.",
                status_code=422,
            )
        return clean_tasks(response.parsed_output)
