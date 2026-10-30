"""Settings for the backend, read from environment variables.

Every setting lives here, so the rest of the code never calls os.getenv()
directly. To see what can be configured, read .env.example in the repo root.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load the .env file from the repo root (two folders up from this file:
# backend/app/config.py -> backend/app -> backend -> repo root).
# Variables that are already set in your shell win over the .env file.
REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / ".env")

# Connection string for Postgres. It contains a password, so there is no
# default value in the code: it has to come from .env.
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. Copy .env.example to .env in the repo root "
        "and fill in your values."
    )

# The frontend's address. Browsers block requests from other origins
# unless the backend allows them (CORS), see app/main.py.
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

# Which Claude model extracts tasks. The API key itself is read by the
# anthropic library straight from ANTHROPIC_API_KEY (see app/claude_extractor.py).
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-opus-5-5")

# Which AI finds the tasks: "gemini" (Google, has a free tier) or "claude".
AI_PROVIDER = os.getenv("AI_PROVIDER", "claude").strip().lower()
if AI_PROVIDER not in ("gemini", "claude"):
    raise RuntimeError(f'AI_PROVIDER must be "gemini" or "claude", not "{AI_PROVIDER}".')

# Gemini settings. Get a key at https://aistudio.google.com/apikey
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or None
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
# Tried once if the main model is overloaded or out of free quota.
# Set it to an empty value to turn the fallback off.
GEMINI_FALLBACK_MODEL = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-3.5-flash-lite") or None
