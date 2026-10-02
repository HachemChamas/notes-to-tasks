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
